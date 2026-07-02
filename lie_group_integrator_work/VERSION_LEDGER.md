# Version Ledger

This file is the human-readable ledger for the exploratory Lie-group integrator
work. The machine-readable source is `version_ledger.csv`; the plot is generated
by `plot_version_ledger.py` as `version_progression.png`. The mathematical
order proof/status record is `ORDER_PROOF_LEDGER.md`.

## Version Tree

```text
paper question: better Lie-group integrator for frictional index-3 MBD
|
+-- representation and baseline reproduction
|   +-- v001_so3_benchmarks
|   +-- v002_cf4_right_order
|   +-- v003_sbel_ra_repro
|
+-- conservative Lie mechanics
|   +-- v004_yoshida_midpoint
|   +-- v005_gauss_lie4
|
+-- constrained fixed-pivot DAE path
|   +-- v006_fixed_pivot_dae
|   +-- v007_absolute_gauss_dae
|   +-- v008_endpoint_constrained_dae
|
+-- friction, Jacobians, and S3 quaternion transport
|   +-- v009_friction_endpoint_dae
|   +-- v010_jax_jacobian_endpoint_dae
|   +-- v011_s3_transport_operator
|   +-- v012_quaternion_endpoint_dae
|
+-- current high-order candidate path
|   +-- v013_gauss6_quaternion_endpoint_dae
|   +-- v014_friction_smoothness_sweep
|   +-- v015_adaptive_gauss64_endpoint
|   +-- v019_lambda_dependent_friction
|   +-- v020_adaptive_lambda_friction
|   +-- v021_brown_mcphee_lambda_friction
|   +-- v022_revolute_brown_mcphee
|
+-- reference-family baselines
    +-- v016_trapezoidal_baseline
    +-- v017_lie_bdf2_baseline
    +-- v018_lobatto_endpoint_baseline
|
+-- full absolute-coordinate lower-pair and sparse-solver path
    +-- v023_absolute_revolute_dae ... v029_double_revolute_pivotva_dae
    +-- v030_double_revolute_jacobian_sparsity ... v038_pattern_cache_reuse
    +-- v039_triple_revolute_scaling ... v042_skew_axis_triple_revolute
    +-- v043_skew_prismatic_lower_pair
    +-- v044_double_prismatic_chain
    +-- v045_row_colored_vjp_prismatic
    +-- v047_cylindrical_chain_pipeline

+-- validation and pipeline anchors
    +-- v046_asme_four_examples_validation
    +-- v048_cross_paper_same_test_benchmarks
```

## Current Best Map

| Target | Current Best | Evidence |
| --- | --- | --- |
| Prescribed SO(3) kinematics | `cf4` / `rkmk4` | v002 corrected right-action fourth-order behavior. |
| Smooth conservative mechanics | `gauss_lie4` | v005 gives near-fourth-order accuracy with strong invariant behavior. |
| Reduced fixed-pivot constrained mechanics | reduced `gauss_lie4` | v006 gives near-fourth-order accuracy with exact reconstructed constraints. |
| Absolute-coordinate endpoint DAE | `absolute_gauss_lie4_endpoint` | v008 removes endpoint projection while keeping near-fourth-order behavior. |
| Smooth frictional quaternion index-3 DAE | `quaternion_gauss_lie6_endpoint_jax` | v013/v014 show near-sixth-order smooth behavior and large error/runtime advantage. |
| Multiplier-dependent nonlinear friction | lambda-friction Gauss6 endpoint residual | v019 shows AD/JAX handles friction depending on Lagrange multipliers without hand Jacobians. |
| High-accuracy near-nonsmooth regularized friction | `adaptive_gauss64_endpoint_jax` | v015 beats globally halving fixed Gauss6 for `eps=0.05` and `eps=0.025`. |
| High-accuracy multiplier-dependent sharp friction | `adaptive_lambda_gauss64_endpoint_jax` | v020 beats globally halving fixed Gauss6 by 51.8x in error at 1.17x runtime. |
| Brown-McPhee-style multiplier-dependent sharp friction | `adaptive_bm_lambda_gauss64_endpoint_jax` | v021 beats globally halving fixed Gauss6 by 4.3x in error at 1.77x runtime. |
| Paper-like revolute Brown-McPhee sharp friction | adaptive revolute Gauss64 | v022 gives 3.072e-11 angle error versus fixed Gauss6 h=0.00625 at 3.246e-07. |
| Paper-style trapezoidal comparison | Gauss6 beats reduced Lie-trapezoidal | v016 shows 10^2-10^7 lower h=0.025 orientation error for Gauss6. |
| BDF-style reference direction | Gauss6 beats reduced Lie-BDF2 for accuracy | v017 shows Lie-BDF2 is a robustness/damping baseline, not an accuracy winner. |
| TFE/Gauss-Lobatto endpoint-node direction | Gauss6 still wins on accuracy-per-cost | v018 shows Lobatto6 is accuracy-competitive but much slower in the reduced benchmark. |
| Larger-topology sparse-AD scaling | triple-revolute Gauss6 FullVA with JVP-pruned sparse AD | v039 shows the sparse-AD backend transfers from the 138D double-revolute residual to a 207D triple-revolute residual with zero dense-validation pattern misses. |
| Production-style triple-revolute pattern acquisition | generated block superset plus JVP pruning | v040 removes v039's full-matrix superset and recovers the exact dense-validation pattern from a generated block superset. |
| Triple-revolute sparse-pattern cache policy | generated-block refresh/union | v041 shows a smooth short cache transfers to longer nominal/perturbed smooth/sharp runs and a stale cache can be repaired without dense Jacobians. |
| Non-coplanar lower-pair geometry | skew-axis triple-revolute FullVA | v042 replaces global-axis revolute constraints with parent-child skew-axis alignment and keeps sparse-AD correctness/speed. |
| Non-revolute lower-pair coverage | skew-axis prismatic FullVA | v043 adds a prismatic sliding joint with Brown-McPhee-style friction; sparse AD is correct but slower at 69D. |
| Interbody non-revolute lower-pair coverage | double-prismatic FullVA | v044 adds a second body and an interbody prismatic joint; sparse AD remains exact but is not yet faster because the pattern needs 90 colors. |
| Prismatic sparse-AD assembly diagnostic | row-colored VJP | v045 reduces the v044 seed count from 90 column colors to 54 row colors, but reverse-mode overhead keeps dense `jacfwd` faster. |
| Four-example ASME validation | upstream SBEL/Negrut rA harness | v046 runs single pendulum, double pendulum, four link, and slider crank as the current validation gate and reproducibility anchor. |
| Cylindrical lower-pair scaffold | two-body cylindrical Gauss6 FullVA | v047 has clean sparse-pattern, endpoint velocity, endpoint-projection audit, and endpoint KKT residual-closure evidence plus high smooth-case convergence after initial velocity compatibility is repaired; the four-example gate is wired to v046 and now has exact single-pendulum driven kinematics, a full absolute-coordinate driven single FullVA residual, an embedded scalar FullVA bridge with reaction reconstruction, accepted double-pendulum FullVA reference policy, a v046 double diagnostic, a reference-floor halving check, a lower-pair graph bridge, a `Phi_q` full-row-rank audit, and accepted local closed-loop kinematic FullVA plus reaction-dynamics rows for four_link/slider_crank. |
| Cross-paper same-test execution | v048 benchmark harness | v048 writes a 17-row external run plan, estimates and executes the full 2021 public order-policy workload, completes all 9/9 `rA/rp/reps` public step-size trio groups for `single_pendulum`, `four_link`, and `slider_crank` as 27/27 ok rows, adds 9/9 public `double_pendulum` dynamic self-reference order rows for `rA/rp/reps`, completes the 12/12 public timing/iteration policy rows for `rA/rp/reps` on all four examples at `T=3`, `h=1e-3`, has a bounded same-mechanism `Gauss6/FullVA` single-pendulum pilot with observed orders `6.073/6.033/6.055/6.024`, adds a 3/3 exact public-horizon `Gauss6/FullVA` single-pendulum step-size trio at `T=3`, `h=[1e-2,1e-3,1e-4]` (roundoff-limited final-error orders), adds 6/6 selected closed-loop `Gauss6/FullVA` residual rows on the 2021 `four_link` and `slider_crank` mechanisms with max dynamics residuals `1.338e-13/6.492e-15`, adds 6/6 public-horizon closed-loop residual rows for the same mechanisms at `T=3`, `h=[1e-2,1e-3,1e-4]` with finest-row max dynamics residuals `5.136e-13/1.113e-14`, adds a coarse-first public-horizon `double_pendulum` `Gauss6/FullVA` tranche at `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`, with position/velocity orders `7.951/7.042` and max endpoint residuals `1.131e-05/3.533e-04`, adds matching coarse same-window public `double_pendulum` baselines where `rA/reps` complete 6/6 rows with position/velocity orders `0.703/0.754` while `rp` records three Newton nonconvergence rows, adds a single-pendulum coarse same-window tranche with 9/9 public rows, 3/3 local `Gauss6/FullVA` rows, and a 4-row work/precision summary at `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`, with local position order `6.054`, adds a 12/12 selected same-window closed-loop comparison table for public `rA` dynamics versus local `Gauss6/FullVA` residual rows at `T=0.2`, `h=[0.02,0.01,0.005]`, adds 9-row public order/work, 4-row same-window work/precision, 3-row double coarse work/precision, 4-row single coarse work/precision, a 2-row closed-loop surrogate dynamic gate, a 2-row closed-loop dynamic error floor audit, a closed-loop coarse dynamic-order probe with `11/12` ok rows and zero accepted dynamic-order rows, and 4-row coarse-first readiness gate CSVs for manuscript tables, writes a 48-row four-example performance matrix with 32 completed and 0 partial rows, adds a bounded 2022 half-implicit four-example pilot with 24/24 ok rows and 8/8 `rA/rA_half` model-form trios, and records an 11-row velocity-partitioning code-path audit covering the EasyChair PDF reference check, public web search, and both local SBEL mirror refs `origin/master` plus `origin/user/aaron/msd`, with 0 exact VP path hits; `same_test_campaign_status` remains `not_run`, `coarse_first_ready_examples=2/4`, `closed_loop_floor_audit_available=2`, and no external superiority claim is made. |

## Version Details

### v001_so3_benchmarks

- Improvement: created the first reproducible SO(3) benchmark suite for
  prescribed rotations and torque-free rigid-body dynamics.
- Evidence: [v001_report.md](v001_so3_benchmarks/results/v001_report.md).
- Role: historical baseline and test harness.
- Limitation: no corrected high-order winner yet.

### v002_cf4_right_order

- Improvement: corrected the right-action commutator-free fourth-order formula.
- Evidence: [v002_report.md](v002_cf4_right_order/results/v002_report.md).
- Role: best prescribed-orientation candidate together with RKMK4.
- Limitation: kinematics only; no constraints, loads, or friction.

### v003_sbel_ra_repro

- Improvement: reproduced the SBEL/Negrut rA-formulation code in a modern `uv`
  environment while keeping the upstream checkout unchanged.
- Evidence: [v003_report.md](v003_sbel_ra_repro/results/v003_report.md).
- Role: reproducibility anchor for the Negrut/Kissel rotation-matrix line.
- Limitation: tested dynamics behavior is roughly first order; not a high-order
  competitor.

### v004_yoshida_midpoint

- Improvement: added a fourth-order Yoshida composition of Lie midpoint.
- Evidence: [v004_report.md](v004_yoshida_midpoint/results/v004_report.md).
- Role: conservative structure-preserving reference.
- Limitation: negative substeps are a bad fit for friction/contact.

### v005_gauss_lie4

- Improvement: added a two-stage Gauss-Legendre body-angular-velocity solve plus
  right-action attitude reconstruction.
- Evidence: [v005_report.md](v005_gauss_lie4/results/v005_report.md).
- Key metric: orientation order 3.987 and omega order 3.989.
- Role: best smooth conservative mechanics prototype.
- Limitation: still unconstrained.

### v006_fixed_pivot_dae

- Improvement: moved Gauss-Lie4 to a fixed-pivot rigid-body DAE prototype with
  exact holonomic reconstruction and recovered multipliers.
- Evidence: [v006_report.md](v006_fixed_pivot_dae/results/v006_report.md).
- Key metric: orientation order 3.986 with exact reconstructed constraints.
- Role: best reduced fixed-pivot constrained mechanics prototype.
- Limitation: reduced DAE, not a full absolute-coordinate Newton solve.

### v007_absolute_gauss_dae

- Improvement: implemented an explicit-multiplier absolute-coordinate stage
  solve and showed position+velocity+acceleration consistency is required.
- Evidence: [v007_report.md](v007_absolute_gauss_dae/results/v007_report.md).
- Key metric: best projected variant reaches orientation order 3.970.
- Role: index-3 DAE consistency lesson.
- Limitation: still used endpoint projection.

### v008_endpoint_constrained_dae

- Improvement: added endpoint variables and endpoint constraints inside the
  nonlinear solve, removing post-step projection.
- Evidence: [v008_report.md](v008_endpoint_constrained_dae/results/v008_report.md).
- Key metric: orientation order 3.970 with endpoint constraints around 1e-16.
- Role: best projection-free absolute-coordinate fixed-pivot prototype.
- Limitation: finite-difference Jacobian cost.

### v009_friction_endpoint_dae

- Improvement: added smooth and sharper Coulomb-like regularized pivot friction.
- Evidence: [v009_report.md](v009_friction_endpoint_dae/results/v009_report.md).
- Key metric: smooth order 3.979/4.009; sharp order drops to 2.462/2.064.
- Role: friction-driven order-reduction evidence.
- Limitation: finite-difference Jacobian and simplified friction torque.

### v010_jax_jacobian_endpoint_dae

- Improvement: replaced finite-difference Newton Jacobians with JAX `jacfwd`.
- Evidence: [v010_report.md](v010_jax_jacobian_endpoint_dae/results/v010_report.md).
- Key metric: roundoff agreement with finite difference and about 30-40x warm
  speedups.
- Role: best nonlinear-solve backend evidence.
- Limitation: still SO(3) local-vector residual.

### v011_s3_transport_operator

- Improvement: implemented the paper's quaternion derivative transport identity
  `Pi(g)=g_p T_exp+g_theta`.
- Evidence: [v011_report.md](v011_s3_transport_operator/results/v011_report.md).
- Key metric: analytic transport matches AD at 1e-16 to 1e-15 scale.
- Role: operator-level bridge to the paper formulation.
- Limitation: isolated operator test.

### v012_quaternion_endpoint_dae

- Improvement: embedded scalar-first unit quaternion right-action update into
  the endpoint-constrained frictional DAE residual.
- Evidence: [v012_report.md](v012_quaternion_endpoint_dae/results/v012_report.md).
- Key metric: matches the prior SO(3) residual to roundoff; smooth order 3.979.
- Role: verified quaternion residual foundation.
- Limitation: still fourth order and still sharp-friction order-reduced.

### v013_gauss6_quaternion_endpoint_dae

- Improvement: added three-stage Gauss-Legendre sixth-order endpoint collocation.
- Evidence: [v013_report.md](v013_gauss6_quaternion_endpoint_dae/results/v013_report.md).
- Key metric: smooth friction orientation order 5.994; h=0.025 smooth error
  drops from Gauss4's 2.868e-07 to 3.066e-11.
- Role: best smooth high-accuracy frictional DAE candidate.
- Limitation: sharp friction remains order-limited; not full TFE/Brown-McPhee.

### v014_friction_smoothness_sweep

- Improvement: swept friction regularization width to identify when Gauss6 is
  worth the extra stages.
- Evidence: [v014_report.md](v014_friction_smoothness_sweep/results/v014_report.md).
- Key metric: Gauss6 is a strong win for `eps=1.0, 0.5, 0.2`; useful at
  `eps=0.1`; marginal at `eps=0.05, 0.025`.
- Role: smoothness decision boundary.
- Limitation: near-nonsmooth behavior needs adaptivity or nonsmooth-aware models.

### v015_adaptive_gauss64_endpoint

- Improvement: added embedded adaptive Gauss6/Gauss4 endpoint control.
- Evidence: [v015_report.md](v015_adaptive_gauss64_endpoint/results/v015_report.md).
- Key metric: for `eps=0.05`, adaptive `tol=1e-6` gives 8.713e-09 in 0.472s;
  for `eps=0.025`, 3.538e-08 in 0.547s.
- Role: best high-accuracy near-nonsmooth regularized-friction candidate.
- Limitation: not the cheapest default and not true nonsmooth contact.

### v016_trapezoidal_baseline

- Improvement: implemented a favorable reduced right-action Lie-trapezoidal
  baseline for paper-style comparison.
- Evidence: [v016_report.md](v016_trapezoidal_baseline/results/v016_report.md).
- Key metric: at h=0.025, Gauss6 is 4.84e7x, 4.16e7x, and 8.57e2x lower
  orientation error for frictionless, smooth-friction, and sharp-friction cases.
- Role: rules out trapezoidal as best candidate in the local benchmark.
- Limitation: reduced baseline only, not a full paper TFE/trapezoidal DAE.

### v017_lie_bdf2_baseline

- Improvement: implements a BLieDF/BDF-style reduced Lie-BDF2 baseline with
  RKMK4 startup.
- Evidence: [v017_report.md](v017_lie_bdf2_baseline/results/v017_report.md).
- Key metric: at h=0.025, Gauss6 is 1.87e8x, 1.60e8x, and 3.20e3x lower
  orientation error than Lie-BDF2 for frictionless, smooth-friction, and
  sharp-friction cases. In a 20s frictionless long run, BDF2 changes energy by
  -5.314e-02 while Gauss6 changes energy by -2.922e-11.
- Role: BDF-style robustness/damping baseline, ruled out as the local
  high-accuracy winner.
- Limitation: this is reduced BDF2, not a full constrained BLieDF/TFE or
  generalized-alpha implementation.

### v018_lobatto_endpoint_baseline

- Improvement: implements reduced Lie-Lobatto endpoint-node collocation to test
  the paper/TFE Gauss-Lobatto direction.
- Evidence: [v018_report.md](v018_lobatto_endpoint_baseline/results/v018_report.md).
- Key metric: Lobatto6 reaches sixth order in smooth cases and is
  accuracy-competitive, but not better on accuracy-per-cost. In smooth friction
  h=0.025, Lobatto6 gives 1.161e-11 in 0.631s versus Gauss6 1.579e-11 in
  0.149s. In sharp friction h=0.025, Gauss6 gives 7.566e-07 in 0.131s versus
  Lobatto6 9.131e-07 in 0.601s.
- Role: TFE-style endpoint-node baseline, ruled out as the current local
  accuracy-per-cost winner.
- Limitation: reduced Lobatto only; Gauss-Lobatto nodes may still matter for
  conditioning in a full absolute-coordinate TFE residual.

### v019_lambda_dependent_friction

- Improvement: adds a multiplier/reaction-load dependent Stribeck-style friction
  torque directly inside the quaternion endpoint DAE residual.
- Evidence: [v019_report.md](v019_lambda_dependent_friction/results/v019_report.md).
- Key metric: smooth lambda-friction Gauss6 reaches orientation order 5.410 and
  h=0.025 error 4.350e-11 versus Gauss4 1.634e-07, a 3.76e3x reduction at 1.20x
  runtime. Sharp lambda-friction still order-reduces, but Gauss6 cuts h=0.025
  error by 3.19x at 1.23x runtime.
- Role: best local evidence that the AD-friendly quaternion endpoint residual
  handles multiplier-dependent nonlinear friction loads.
- Limitation: simplified Stribeck-like pivot friction, not exact Brown-McPhee
  revolute friction or contact complementarity.

### v020_adaptive_lambda_friction

- Improvement: combines v015 embedded adaptive Gauss6/Gauss4 endpoint control
  with v019 multiplier-dependent Stribeck-style friction.
- Evidence: [v020_report.md](v020_adaptive_lambda_friction/results/v020_report.md).
- Key metric: in sharp lambda-friction, adaptive `tol=1e-7` reaches 2.666e-10
  orientation error versus fixed Gauss6 h=0.0125 error 1.381e-08, a 51.8x
  reduction at 1.17x runtime. Looser `tol=1e-5` beats coarse fixed Gauss6
  h=0.025 by about 5.00x error within 1.09x runtime.
- Role: best high-accuracy multiplier-dependent sharp-friction candidate.
- Limitation: smooth lambda-friction does not need this adaptivity, and the
  friction law is still smooth regularized friction rather than complementarity.

### v021_brown_mcphee_lambda_friction

- Improvement: replaces v019's Gaussian/tanh friction load with a
  Brown-McPhee-style continuous velocity curve while retaining lambda-scaled
  normal load and the quaternion endpoint DAE residual.
- Evidence: [v021_report.md](v021_brown_mcphee_lambda_friction/results/v021_report.md).
- Key metric: smooth Brown-McPhee friction keeps fixed Gauss6 as the clean
  default; fixed h=0.0125 gives 1.088e-11 orientation error. Sharp
  Brown-McPhee friction order-reduces, but adaptive `tol=1e-7` reaches
  1.186e-07 orientation error versus fixed Gauss6 h=0.0125 error 5.128e-07,
  a 4.3x reduction at 1.77x runtime.
- Role: best local Brown-McPhee-style multiplier-dependent sharp-friction
  candidate.
- Limitation: componentwise fixed-pivot surrogate, not exact revolute-joint
  Brown-McPhee friction or nonsmooth stick-slip complementarity.

### v022_revolute_brown_mcphee

- Improvement: adds a paper-like one-DOF revolute pendulum benchmark with
  Brown-McPhee continuous velocity friction, quaternion output, and
  reaction-load-dependent friction.
- Evidence: [v022_report.md](v022_revolute_brown_mcphee/results/v022_report.md).
- Key metric: smooth revolute Brown-McPhee friction gives Gauss6 observed angle
  order 5.773, with fixed h=0.00625 and adaptive `tol=1e-8` essentially tied
  near 2.8e-12 error. Sharp revolute Brown-McPhee friction drops fixed Gauss6
  to observed order 2.412, while adaptive `tol=1e-7` reaches 3.072e-11 angle
  error versus fixed Gauss6 h=0.00625 error 3.246e-07.
- Role: best paper-like revolute Brown-McPhee sharp-friction evidence.
- Limitation: reduced one-DOF model, not a full absolute-coordinate index-3
  revolute DAE or complementarity stick-slip model.

### v023_absolute_revolute_dae

- Improvement: upgrades the revolute Brown-McPhee pendulum from a reduced
  scalar coordinate to a full absolute-coordinate quaternion DAE with five
  explicit revolute constraints and stage Lagrange multipliers.
- Evidence: [v023_report.md](v023_absolute_revolute_dae/results/v023_report.md).
- Key metric: in the smooth absolute-coordinate revolute DAE, Gauss6 h=0.0125
  gives 1.111e-07 orientation error versus Gauss4's 6.306e-01. In the sharp
  Brown-McPhee case, Gauss6 h=0.0125 still gives 4.473e-07 orientation error,
  while Gauss4 fails at h=0.025 and h=0.0125.
- Role: first full absolute-coordinate revolute DAE robustness/fidelity test.
- Limitation: this version intentionally has no endpoint projection; endpoint
  position drift is small for Gauss6, but endpoint velocity drift remains
  visible, so endpoint/velocity/acceleration constraint treatment is the next
  formulation target.

### v024_absolute_revolute_lobatto_dae

- Improvement: tests the Gauss-Lobatto/TFE-inspired direct endpoint-node
  collocation idea on the full v023 absolute-coordinate revolute residual.
- Evidence: [v024_report.md](v024_absolute_revolute_lobatto_dae/results/v024_report.md).
- Key metric: direct Lobatto4 and Lobatto6 fail for every smooth and sharp
  fixed-step run, even after adding zero-safe JAX Lie differentials for the
  `c=0` node and a damped rank-deficient Newton fallback. The Gauss6 baseline
  still succeeds, with smooth h=0.0125 orientation error 1.111e-07 and sharp
  h=0.0125 orientation error 4.473e-07.
- Role: negative result ruling out a simple Gauss-to-Lobatto node swap as the
  missing full-DAE improvement.
- Limitation: this is not a full implementation of the paper's TFE weighted
  residual formulation; it only tests direct Lobatto collocation on the same
  stage residual.

### v025_absolute_revolute_projected_dae

- Improvement: adds SHAKE/RATTLE-style endpoint projection to the v023 full
  absolute-coordinate revolute residual.
- Evidence: [v025_report.md](v025_absolute_revolute_projected_dae/results/v025_report.md).
- Key metric: projected Gauss6 enforces endpoint position and velocity
  constraints to zero in both smooth and sharp Brown-McPhee cases. In the sharp
  case, projection rescues Gauss4 at h=0.025 and h=0.0125, where raw Gauss4
  fails. The tradeoff is accuracy: projected Gauss6 h=0.0125 has orientation
  error 3.899e-06 in the sharp case versus raw Gauss6's 1.389e-06 relative to
  the projected fine-step reference.
- Role: practical endpoint-closure repair for the full revolute DAE prototype.
- Limitation: projection changes the subsequent trajectory; it is not a full
  TFE/index-3 weighted-residual formulation.

### v026_absolute_revolute_stage_velocity_dae

- Improvement: moves part of the constraint repair inside Newton by replacing
  stage `r` collocation with a square pivot-velocity constraint residual.
- Evidence: [v026_report.md](v026_absolute_revolute_stage_velocity_dae/results/v026_report.md).
- Key metric: Gauss6 PivotVC reduces endpoint velocity drift from 2.663e-03 to
  6.897e-08 in the smooth h=0.0125 case, and from 2.325e-03 to 9.580e-08 in
  the sharp h=0.0125 case. It also rescues Gauss4 in the sharp h=0.025 and
  h=0.0125 runs where raw Gauss4 fails.
- Role: best non-projection full absolute-coordinate revolute DAE repair so far.
- Limitation: only the pivot velocity part of the lower-pair velocity
  consistency is enforced; full hinge-axis velocity/acceleration and TFE
  weighted-residual treatment remain open.

### v027_absolute_revolute_stage_acceleration_dae

- Improvement: strengthens v026 by replacing stage `v` collocation with the
  pivot acceleration constraint while keeping the full revolute Newton system
  square.
- Evidence: [v027_report.md](v027_absolute_revolute_stage_acceleration_dae/results/v027_report.md).
- Key metric: Gauss6 PivotVA h=0.0125 reduces endpoint velocity drift to
  5.213e-13 in the smooth Brown-McPhee case and 1.570e-12 in the sharp case,
  while stage pivot acceleration is enforced at about 1e-15. This is about
  five orders tighter than v026 PivotVC velocity drift, with essentially the
  same Gauss6 orientation error.
- Role: best non-projection full absolute-coordinate revolute DAE consistency
  repair tested so far.
- Limitation: this proves the pivot acceleration repair on a one-DOF revolute
  pendulum; full lower-pair acceleration consistency and TFE weighted-residual
  treatment for larger multibody systems remain open.

### v028_offaxis_revolute_full_axis_dae

- Improvement: adds an off-axis body-torque stress test and a FullVA residual
  that explicitly enforces hinge-axis velocity and acceleration components
  while keeping the revolute Newton system square.
- Evidence: [v028_report.md](v028_offaxis_revolute_full_axis_dae/results/v028_report.md).
- Key metric: in the smooth h=0.0125 Gauss6 test, FullVA reduces stage axis
  acceleration from PivotVA's 6.670e-12 to 1.867e-25, with identical
  orientation error 4.888e-10. In the sharp h=0.0125 test, FullVA reduces stage
  axis acceleration from 5.163e-12 to 2.095e-25, again with identical
  orientation error 5.265e-07.
- Role: off-axis constrained-torque stress test showing that explicit axis
  consistency is possible, but not the trajectory bottleneck in the one-DOF
  revolute pendulum.
- Limitation: a neutral/negative result for this single-joint benchmark; the
  next useful step is multi-joint/general lower-pair treatment, not more
  single-axis polishing.

### v029_double_revolute_pivotva_dae

- Improvement: applies the square PivotVA/FullVA residual idea to a two-body
  absolute-coordinate double-revolute chain with ground and interbody
  Brown-McPhee friction.
- Evidence: [v029_report.md](v029_double_revolute_pivotva_dae/results/v029_report.md).
- Key metric: in the smooth h=0.02 Gauss6 run, PivotVA reduces endpoint
  velocity drift from raw 1.807e-04 to 7.745e-13 and cuts orientation error
  from 4.105e-09 to 2.111e-09. In the sharp h=0.02 Gauss6 run, PivotVA reduces
  endpoint velocity drift from raw 1.279e-04 to 1.107e-11 while preserving
  trajectory error. FullVA drives axis acceleration diagnostics to about
  1e-26 but does not change trajectory relative to PivotVA.
- Role: first local evidence that the v027 PivotVA repair generalizes from a
  one-body revolute pendulum to an interbody revolute joint.
- Limitation: the model is still planar and the computational cost wall is
  visible: Gauss6 double-revolute runs take several seconds because each
  Newton Jacobian is 138 by 138. Sparse/block linear algebra is the next
  scaling target.

### v030_double_revolute_jacobian_sparsity

- Improvement: diagnoses the dense Newton cost wall from v029 by measuring
  Jacobian sparsity, conditioning, dense solve time, and generic CSR sparse
  solve time on converged first-step double-revolute systems.
- Evidence: [v030_report.md](v030_double_revolute_jacobian_sparsity/results/v030_report.md).
- Key metric: Gauss6 FullVA Jacobians are 138 by 138 but only about 3.06%
  dense. In this environment, smooth Gauss6 FullVA dense solve time is
  2.419e-01s versus CSR `spsolve` 1.193e-04s; sharp Gauss6 FullVA dense solve
  time is 3.126e-01s versus CSR 5.668e-04s. Gauss4 92-dimensional systems are
  too small for CSR to always beat dense solve overhead.
- Role: turns the v029 cost complaint into a concrete solver direction:
  integrate sparse/block linear solves into the Gauss6 Newton loop.
- Limitation: v030 still materializes a dense AD Jacobian before converting to
  CSR. The deeper scalability target is structured sparse AD, block assembly,
  or matrix-free Newton-Krylov.

### v031_sparse_newton_double_revolute

- Improvement: moves the v030 sparse-solve diagnostic into the actual
  double-revolute Newton loop by replacing dense `numpy.linalg.solve` with
  thresholded CSR `scipy.sparse.linalg.spsolve`.
- Evidence: [v031_report.md](v031_sparse_newton_double_revolute/results/v031_report.md).
- Key metric: in the smooth Gauss6 FullVA h=0.02, T=0.10 run, runtime drops
  from dense 3.408s to CSR 0.109s, a 31.35x end-to-end speedup; Newton
  linear-solve time drops 202.76x. In the sharp Gauss6 FullVA run, runtime
  drops from 2.838s to 0.129s, a 22.02x speedup. The worst dense-vs-CSR final
  orientation difference across the tested runs is 3.405e-23 rad.
- Role: first implementation evidence that the successful full-DAE Gauss6
  residual can be made much faster by sparse Newton linear algebra without
  changing the trajectory.
- Limitation: v031 still materializes a dense JAX Jacobian and only converts it
  to CSR before the linear solve. The next scalability target is structured
  sparse/block AD assembly or matrix-free Newton-Krylov on a larger topology.

### v032_matrix_free_newton_krylov

- Improvement: tests whether the v031 dense-Jacobian materialization bottleneck
  can be avoided by using JAX Jacobian-vector products and unpreconditioned
  GMRES for the Gauss6 FullVA Newton systems.
- Evidence: [v032_report.md](v032_matrix_free_newton_krylov/results/v032_report.md).
- Key metric: JVP consistency is correct: relative error versus dense
  Jacobian-vector products is 1.803e-16 in the smooth case and 5.233e-16 in the
  sharp case. However, unpreconditioned GMRES fails after 200 iterations with
  linear residual 1.323e+00 in the smooth case and 1.574e+00 in the sharp case,
  while the v031 CSR direct path solves the same single-step systems in
  0.017-0.023s.
- Role: useful negative result. It rules out plain matrix-free GMRES as the
  next solver-scaling move and points to preconditioned Krylov or structured
  sparse/block Jacobian assembly.
- Limitation: no preconditioner yet, and the test is single-step Gauss6 FullVA
  on the planar double-revolute chain. v031 CSR direct sparse Newton remains
  the best implemented scaling path.

### v033_lagged_sparse_newton

- Improvement: tests modified sparse Newton as a cheaper alternative to
  refreshing the CSR Jacobian at every Newton correction.
- Evidence: [v033_report.md](v033_lagged_sparse_newton/results/v033_report.md).
- Key metric: lagged variants preserve the final trajectory to about
  1e-15 orientation difference and reduce Jacobian evaluations by 1.45x-3.2x.
  However, the saving is offset by extra Newton corrections, residual
  evaluations, and sparse solves. The best speedup is only 1.06x for sharp
  Gauss6 PivotVA with two-correction lagging; most variants are slower than
  fresh CSR.
- Role: useful neutral/negative result. It shows simple Jacobian lagging is
  numerically safe on the targeted double-revolute test, but not a strong
  scaling solution for this system.
- Limitation: still materializes dense Jacobians whenever refreshed. v031 fresh
  CSR remains the best default; the next real target is structured sparse/block
  assembly or a preconditioner.

### v034_colored_jvp_sparse_jacobian

- Improvement: implements a structured sparse-AD proof of concept using
  column coloring and JAX JVPs to assemble only sparse Jacobian values for the
  Gauss6 FullVA double-revolute residual.
- Evidence: [v034_report.md](v034_colored_jvp_sparse_jacobian/results/v034_report.md).
- Key metric: the warm-up union pattern has 582 nonzeros, about 3.06% density,
  and 11 column colors. Colored JVP assembly matches dense Jacobian values with
  max relative error 1.932e-18 in the smooth case and 1.003e-16 in the sharp
  case; trajectory differences versus dense-Jacobian CSR are essentially
  roundoff. Runtime is worse on the small 138D system: 0.428-0.432s for colored
  JVP versus 0.048-0.064s for dense `jacfwd` CSR.
- Role: correct structured sparse-AD demonstration. It shows the sparse
  derivative route is viable, but generic Python-level coloring is not the
  small-system speed winner.
- Limitation: the pattern is obtained from a dense warm-up Newton path and
  colored assembly pays 11 separate JVP calls per Jacobian. The next target is
  hand/block sparse assembly, compiled/batched coloring, or a larger topology
  where dense `jacfwd` memory/cost becomes decisive.

### v035_batched_colored_jvp

- Improvement: replaces v034's one-JVP-per-color sparse Jacobian assembly with
  one compiled `vmap(jvp)` batch over all colored seed vectors.
- Evidence: [v035_report.md](v035_batched_colored_jvp/results/v035_report.md).
- Key metric: the same 582-entry, 11-color sparsity pattern matches dense
  Jacobian values to 4.513e-18 relative error in the smooth case and
  4.531e-18 in the sharp case. Batched colored JVP cuts runtime to 0.038s
  smooth and 0.035s sharp, versus dense `jacfwd` CSR at 0.102s and 0.088s.
  That is a 2.66x speedup in smooth friction and 2.49x in sharp friction, with
  trajectory differences at roundoff scale.
- Role: first positive structured sparse-AD Newton backend. It keeps v031's
  sparse solve advantage, avoids dense Jacobian materialization in the timed
  solver loop, and is faster than dense `jacfwd` even on the small 138D
  double-revolute residual.
- Limitation: the sparsity mask still comes from a dense warm-up Newton path.
  The next step is symbolic/block sparsity generation for revolute-chain or
  lower-pair families, then larger topologies where dense Jacobian memory cost
  matters more.

### v036_symbolic_block_pattern

- Improvement: replaces v035's dense warm-up sparsity discovery with a
  conservative hand-derived block-symbolic pattern for the v029 Gauss6 FullVA
  residual.
- Evidence: [v036_report.md](v036_symbolic_block_pattern/results/v036_report.md).
- Key metric: the block-symbolic mask has 1755 entries and 34 colors, compared
  with the warm-up union pattern's 582 entries and 11 colors. It misses zero
  dense entries in the diagnostics, matches dense Jacobian values to about
  3.8e-18 relative error, and preserves the trajectory at roundoff scale. The
  block pattern builds in 0.001-0.003s, versus 1.861-4.186s for dense warm-up
  pattern discovery. The sharp-friction block-symbolic run is 0.050s versus
  dense `jacfwd` CSR at 0.079s; the smooth run is essentially tied, 0.077s
  versus 0.080s, while avoiding the dense warm-up dependency.
- Role: first production-style sparse-AD pattern path. v035 made colored AD
  fast; v036 removes the need to discover the pattern by materializing dense
  Jacobians on a warm-up trajectory.
- Limitation: the block pattern is conservative and overcolored. The next
  target is a finer component-symbolic or generated block pattern, then
  validation on larger revolute chains or less planar lower-pair systems.

### v037_jvp_pruned_symbolic_pattern

- Improvement: uses the v036 block-symbolic mask as a safe superset, then
  prunes it with batched JVPs along a short Newton/trajectory dry-run instead
  of materializing dense Jacobians.
- Evidence: [v037_report.md](v037_jvp_pruned_symbolic_pattern/results/v037_report.md).
- Key metric: in both smooth and sharp cases, the JVP-pruned pattern exactly
  matches the dense warm-up union pattern: 582 entries, 11 colors, zero extra
  entries, and zero missing entries. Pattern construction takes 0.053-0.067s,
  compared with 0.952-1.082s for dense warm-up discovery in the same run. The
  pruned-pattern Jacobian matches dense values to 4.513e-18 smooth and
  4.531e-18 sharp relative error, with roundoff trajectory agreement.
- Role: best current sparse pattern discovery path. v036 provides a safe
  production-style superset; v037 recovers the fine observed pattern using only
  residual values, batched JVPs, and sparse solves.
- Limitation: the pruned pattern is still path-sampled, not a formal symbolic
  proof for all configurations. The next step is larger-chain validation and a
  pattern cache/reuse policy, or automatic symbolic/component tracing.

### v038_pattern_cache_reuse

- Improvement: tests the production policy suggested by v037: discover a fine
  sparse pattern once with JVP pruning, cache it, and reuse it for subsequent
  solves without dense Jacobian discovery.
- Evidence: [v038_report.md](v038_pattern_cache_reuse/results/v038_report.md).
- Key metric: one cached pattern discovered from the smooth case over T=0.06
  has 582 entries and 11 colors. Reused over T=0.12, it misses zero entries
  against dense validation patterns in both smooth and sharp cases. Dense
  validation pattern construction takes 1.733s smooth and 2.043s sharp, while
  the cached pattern was built once in 0.057s. Runtime is dense `jacfwd` CSR
  0.097s vs cached JVP-pruned 0.065s in smooth and 0.101s vs 0.068s in sharp,
  a 1.49x speedup in both cases with roundoff trajectory agreement.
- Role: best current production sparse-AD policy for the double-revolute
  benchmark. It combines v036's safe symbolic superset, v037's dense-free
  pruning, and reuse across friction regimes.
- Limitation: the cache has only been validated on the planar double-revolute
  benchmark and T=0.12. The next step is larger chains, broader state coverage,
  and refresh/union rules for cache misses.

### v039_triple_revolute_scaling

- Improvement: extends the full Gauss6 FullVA sparse-AD benchmark from a
  two-body double-revolute chain to a real three-body triple-revolute chain
  with Brown-McPhee friction at every hinge.
- Evidence: [v039_report.md](v039_triple_revolute_scaling/results/v039_report.md).
- Key metric: the Newton system grows from 138 to 207 variables. The
  JVP-pruned pattern has 930 entries and 11 colors, exactly matching dense
  validation in both smooth and sharp cases with zero missing and zero extra
  entries. Runtime is dense `jacfwd` CSR 0.078s versus cached/JVP-pruned
  0.055s in the smooth case, and 0.097s versus 0.058s in the sharp case,
  giving 1.41x and 1.67x speedups with roundoff trajectory agreement and
  endpoint velocity around 1e-12 to 1e-11.
- Role: first evidence that the sparse-AD/backend improvement transfers to a
  real larger multibody topology, not only the planar double-revolute
  benchmark.
- Limitation: the initial v039 pattern discovery uses a full superset, and the
  smooth build includes the first full-superset JVP compilation. The next step
  is a generated block superset/cache and larger-chain validation.

### v040_generated_block_triple_pattern

- Improvement: replaces v039's temporary full-matrix superset with a generated
  block-dependency superset for the same three-body triple-revolute Gauss6
  FullVA residual.
- Evidence: [v040_report.md](v040_generated_block_triple_pattern/results/v040_report.md).
- Key metric: the generated block superset has 2691 entries and 32 colors,
  with zero dense-validation misses in both smooth and sharp cases. JVP
  pruning inside that superset recovers the exact dense-validation pattern:
  930 entries, 11 colors, zero missing, and zero extra. Runtime is dense
  `jacfwd` CSR 0.104s versus block-pruned 0.049s in the smooth case, and
  0.088s versus 0.049s in the sharp case, giving 2.14x and 1.78x speedups with
  roundoff trajectory agreement.
- Role: best current production-style sparse-pattern acquisition path for the
  triple-revolute benchmark. It shows larger-topology sparse AD no longer needs
  a dense full superset to discover a fine pattern.
- Limitation: still path-sampled on a short planar triple-revolute horizon.
  Needs cache refresh/union rules, longer state coverage, and less-planar or
  more varied lower-pair validation.

### v041_triple_pattern_cache_refresh

- Improvement: turns v040's generated block-pruned pattern into a production
  cache policy: discover once, scan later trajectories inside the generated
  block superset with batched JVPs, and union any newly active entries.
- Evidence: [v041_report.md](v041_triple_pattern_cache_refresh/results/v041_report.md).
- Key metric: a smooth short 930-entry/11-color cache transfers to four longer
  T=0.12 nominal/perturbed smooth/sharp scenarios with zero refresh additions
  and zero dense-validation misses. A stale-cache audit intentionally removes
  23 entries; the generated-block refresh scan finds all 23 and restores the
  final cache to 930 entries with zero dense-validation misses. Cached runtime
  is 1.08x-1.54x faster than dense `jacfwd` CSR across the longer scenarios.
- Role: best current production policy for the triple-revolute sparse-AD
  backend. Dense Jacobians are kept as validation evidence, while refresh uses
  generated block sparsity plus batched JVPs.
- Limitation: still planar triple-revolute only. Needs less-planar lower-pair
  systems, larger chains, and eventually contact or nonsmooth friction cases.

### v042_skew_axis_triple_revolute

- Improvement: replaces the planar/global-axis triple-revolute constraints with
  non-coplanar parent-child axis alignment. Each interbody joint constrains the
  child proximal axis to the parent body's distal axis, so the axis rows depend
  on both parent and child orientations.
- Evidence: [v042_report.md](v042_skew_axis_triple_revolute/results/v042_report.md).
- Key metric: the generated block superset has 2907 entries and 32 colors with
  zero dense-validation misses. JVP pruning recovers the exact dense-validation
  pattern: 2181 entries, 31 colors, zero missing, and zero extra. Runtime is
  dense `jacfwd` CSR 0.094s versus sparse 0.048s in the smooth case, and
  0.099s versus 0.051s in the sharp case, giving 1.98x and 1.94x speedups.
  Endpoint velocity constraints are around 1e-16 after enforcing compatible
  initial interbody axis rates.
- Role: best current evidence that the quaternion Gauss6 FullVA plus sparse-AD
  backend extends beyond planar revolute chains to non-coplanar lower-pair
  geometry.
- Limitation: still a short-horizon three-body revolute test. Needs larger
  skew-axis chains and other lower pairs such as cylindrical or prismatic
  joints.

### v043_skew_prismatic_lower_pair

- Improvement: adds the first non-revolute lower-pair test: a skew-axis
  prismatic joint with five constraints, one free sliding coordinate, and
  Brown-McPhee-style sliding friction coupled to the normal constraint load.
- Evidence: [v043_report.md](v043_skew_prismatic_lower_pair/results/v043_report.md).
- Key metric: the 69D Gauss6 FullVA prismatic residual has a generated block
  superset with 1026 entries and 24 colors, with zero dense-validation misses.
  JVP pruning recovers the exact 414-entry, 18-color dense pattern in both
  smooth and sharp cases. Dense and sparse trajectories match exactly; endpoint
  velocity constraints are 2.3e-17 to 3.4e-17 and orientation acceleration
  constraints are near zero.
- Role: first coverage of a prismatic lower-pair formulation in the local
  quaternion Gauss6 FullVA plus sparse-AD sequence, including zero-safe Lie
  differentials for exactly-zero orientation increments.
- Limitation: sparse JVP is slower than dense `jacfwd` on this 69D small system:
  0.086-0.092s sparse versus 0.054-0.058s dense. It needs interbody
  prismatic/cylindrical chains before supporting a solver-scaling claim.

### v044_double_prismatic_chain

- Improvement: extends v043 to a two-body chain with one ground prismatic joint
  and one interbody prismatic joint, so the second sliding constraint couples
  parent and child positions, velocities, orientations, reaction forces, and
  friction loads.
- Evidence: [v044_report.md](v044_double_prismatic_chain/results/v044_report.md).
- Key metric: the 138D Gauss6 FullVA double-prismatic residual has a generated
  block superset with 4824 entries and 90 colors, with zero dense-validation
  misses. JVP pruning recovers the exact 2439-entry, 90-color dense pattern in
  both smooth and sharp cases. Dense and sparse trajectories match to roundoff;
  endpoint velocity constraints are 8.7e-17 to 9.5e-17.
- Role: first interbody non-revolute lower-pair coverage for the local
  quaternion Gauss6 FullVA plus sparse-AD path.
- Limitation: warmed sparse JVP is slower than dense `jacfwd` on this 138D
  system: dense/sparse is 0.80x smooth and 0.87x sharp. The pattern is exact,
  but 90 colors make the sparse backend too expensive; the next solver work is
  finer coloring/block assembly or a larger rotating-axis chain.

### v045_row_colored_vjp_prismatic

- Improvement: keeps the v044 double-prismatic residual and exact 2439-entry
  sparse pattern, but assembles the sparse Jacobian by row-colored batched VJP
  instead of column-colored batched JVP.
- Evidence: [v045_report.md](v045_row_colored_vjp_prismatic/results/v045_report.md).
- Key metric: row coloring reduces seed directions from 90 column colors to
  54 row colors. The row-VJP Jacobian matches dense `jacfwd` to roundoff in the
  sanity check, and the integrated row-VJP trajectory matches dense to
  roundoff. Smooth row-VJP runtime is 0.129s versus 0.134s for column-JVP, a
  1.04x improvement; sharp row-VJP is effectively tied with column-JVP.
- Role: best current diagnostic of the v044 sparse-AD bottleneck. It proves the
  color count can be reduced, but also shows reverse-mode overhead prevents this
  from becoming a dense-`jacfwd` speed win on the 138D system.
- Limitation: still slower than dense `jacfwd` in both smooth and sharp cases.
  The next implementation target is component/block assembly or larger systems
  where the row-VJP overhead amortizes.

### v046_asme_four_examples_validation

- Improvement: validates the upstream SBEL/Negrut 2021 ASME rA formulation on
  all four local example mechanisms: single pendulum, double pendulum, four
  link, and slider crank.
- Evidence: [v046_report.md](v046_asme_four_examples_validation/results/v046_report.md).
- Key metric: with h=[0.02, 0.01, 0.005] and h=0.001 references, the double
  pendulum passes the strict constraint checks with position order 1.124,
  velocity order 1.141, and acceleration order 1.105. The other three examples
  expose constraint or SO(3) tolerance failures in the recorded upstream path.
- Role: current four-example validation anchor and baseline harness for future
  method versions.
- Limitation: this is a reproducibility and validation-gate version, not a new
  local Gauss6/FullVA method, source-paper superiority claim, or external
  same-test comparison.

### v047_cylindrical_chain_pipeline

- Improvement: promotes the pending cylindrical-chain scratch into a formal
  version and replaces v044's twist-locked prismatic joints with cylindrical
  joints that allow axial sliding and relative spin about the moving axis.
- Evidence: [v047_report.md](v047_cylindrical_chain_pipeline/results/v047_report.md) and
  [validate_v047_outputs.py](v047_cylindrical_chain_pipeline/validate_v047_outputs.py).
- Paper-facing claim boundary: v047 is now framed as a conditional formal-order
  comparison, not as a full source-paper residual reproduction, source-policy
  superiority, or work-precision claim. The accepted Gauss6/FullVA path is
  sixth order, records smooth position/velocity orders 7.161/7.066, and is
  compared only with the local paper-style `m=3` Gauss-Lobatto TFE formula
  target of expected order five. It has four-example coverage with
  dynamic-order evidence on single/double pendulum plus closed-loop
  residual/reaction evidence on four-link/slider-crank.
  `paper_v047_cylindrical_chain/ORDER_ACCEPTANCE_GATE.md` keeps single/double
  as accepted dynamic-order rows and four-link/slider-crank as coverage-only
  for external dynamic order; the local paper-style `m=3`
  Gauss-Lobatto TFE formula target has expected order five. The independent
  full-TFE replacement remains a stronger optional reproduction gate and stays
  open. The strict theorem proof is closed only by the direct 132-row
  residual-bridge/Kantorovich route; it does not close the separate
  primitive/Taylor certificate route, discharge the retained P6 solver-policy
  condition, prove a P7 residual-to-error transfer, or make the global
  source-policy submission package ready.
- Key metric: the 132D Gauss6 FullVA cylindrical residual has a generated block
  superset with 5760 entries and 90 colors with zero dense-validation misses.
  JVP pruning recovers the exact 2637-entry, 90-color dense-validation pattern
  in both smooth and sharp cases. Dense and sparse trajectories match to
  roundoff, and a post-step least-squares velocity projection closes endpoint
  velocity constraints to about 2e-16. The endpoint-projection audit measures
  raw endpoint velocity residual/correction orders 5.817/5.796 for smooth and
  4.089/4.202 for sharp. An augmented endpoint KKT residual closure now solves
  endpoint velocity variables, least-squares stationarity, and endpoint
  velocity constraints as a square residual with the stage equations; it keeps
  smooth/sharp position-velocity orders 7.161/7.066 and 1.894/2.683, with max
  KKT residuals 6.49e-14/5.72e-12 and endpoint velocity residuals below
  3.8e-16. The endpoint TFE gap audit records finest KKT/projection correction
  ratios 0.213 smooth and 0.999 sharp, with closure gains 1.79e1 and 3.56e3,
  while explicitly flagging that stage equations are not yet TFE-weighted. The
  endpoint TFE candidate audit evaluates endpoint-node weighted rows on the
  KKT h-sweep, with max candidate residuals 1.177e-12 smooth and 5.723e-13
  sharp. The solved endpoint-node candidate audit solves those rows inside a
  square Newton residual with max solved residuals 6.643e-14 smooth and
  5.723e-12 sharp while stage equations remain non-TFE-weighted. The
  stage-weighted candidate premultiplies each Gauss6 FullVA stage block by
  sqrt(h*b_i), with max weighted residuals 6.819e-15 smooth and 3.017e-13
  sharp, while remaining diagonal-equivalent to the Gauss6 equations. The
  stage-functional specification audit records six independent weak/TFE row
  families totaling the 132-row stage budget; the implementation audit now
  assembles those rows over the smooth/sharp h-sweep with max equivalence norm
  1.755e-17 while remaining Gauss6-equivalent rather than full TFE. The
  stage-replacement design audit records the 132-row stage budget, the solved
  40-row endpoint extension, the diagonal-equivalent weighting limitation, the
  new implementation audit, the non-equivalent stage probe audit, the boundary-source audit, the source-budget audit, the dominant-source split audit, the component-activation audit, the component-formula audit, the Newton-Euler formula audit, the all-source formula audit, the all-source trajectory bridge audit, the probe-order audit, the solved
  non-equivalent stage-probe audit, the stage-probe homotopy audit, the
  stage-probe block-activation audit, the stage-probe all-source trajectory bridge audit, the stage-probe coupled-budget audit, the stage-probe trajectory-accumulation audit, the stage-probe beta-trajectory bridge audit, and the
  future acceptance gate for the independent residual.
  The paper formula mapping audit encodes the m=3 Gauss-Lobatto Eq. 43
  alpha/beta/gamma map, and the paper derivative-operator audit verifies the
  x-to-y/z map over the 6N+C augmented dimension with max quadratic y/z
  reproduction errors 9.09e-15/6.98e-12. The paper stage-input-map audit maps
  that operator onto all 132 v047 stage rows across six weak row families, and
  the paper multiplier-policy audit specifies lambda_x/lambda_yz dimensions
  24/48 with no extra lambda_y/z residual rows. The paper kinematic-formula
  audit derives four kinematic row-family formulas across 72 stage rows with
  max formula residual 7.26e-18, but does not substitute them into Newton. The
  paper balance/constraint-formula audit derives the remaining Newton-Euler
  weak-balance and lower-pair constraint row-family formulas across 60 stage
  rows with max formula residual 4.34e-19, but does not substitute them into
  Newton. The paper position-substitution candidate replaces the two paper
  position row families inside Newton, covering 36 stage rows with max residual
  5.68e-12 and full rank 132, but its smooth/sharp position-velocity orders
  1.227/0.731 and 1.165/2.464 are order-limited. The paper
  kinematic-substitution candidate replaces all four paper kinematic row
  families inside Newton, covering 72 stage rows with max residual 9.57e-12,
  full rank 132, max condition 8.81e11, and smooth/sharp position-velocity
  orders 1.406/1.542 and 1.400/1.237; it remains diagnostic-z0/order-limited.
  The paper
  all-row substitution candidate combines all six paper row families in one
  132-row Newton residual, with max residual 9.64e-12, full rank 132, max
  condition 1.62e13, and smooth/sharp position-velocity orders 1.406/1.542 and
  1.400/1.237; it remains diagnostic-z0/order-limited and not accepted as full
  TFE. The paper all-row Gauss-z0 diagnostic repeats the six-family/132-row
  substitution with a baseline-Gauss extrapolated start acceleration, giving
  max residual 7.70e-12, full rank 132, max condition 1.58e13, max z0 delta
  1.69e1, and smooth/sharp orders 1.410/1.573 and 1.395/1.170; this shows the
  low-order blocker is not removed by replacing the axis-projected z0 heuristic
  alone. The paper all-row Gauss-z0 terminal-output diagnostic solves the same
  six-family/132-row residual but reads the next state from the terminal paper
  Lobatto node, with max residual 9.20e-12, full rank 132, max condition
  1.58e13, terminal-vs-Gauss output position/velocity deltas 3.19e-03/1.82e-02,
  and smooth/sharp orders 2.494/1.780 and 1.029/0.107; this quantifies
  output-node sensitivity but still does not recover an accepted full TFE
  replacement. The paper all-row recurrent-z0 terminal-output diagnostic keeps
  the same residual and paper terminal output but feeds each terminal paper z
  value into the next step after one Gauss bootstrap, giving max residual
  9.09e-12, full rank 132, max condition 1.58e13, max used-z0-vs-Gauss delta
  4.16e-01, and smooth/sharp orders 4.557/4.667 and 2.579/1.925 while still
  leaving order and conditioning caveats open. The paper all-row consistent-z0
  terminal-output diagnostic removes that bootstrap by solving the
  instantaneous 20D acceleration/multiplier system, with initial residual
  5.94e-15, rank/condition 20/1.66e1, bootstrap count 0, max residual
  9.79e-12, max condition 1.58e13, and smooth/sharp orders 4.046/4.420 and
  2.554/1.918; it isolates the bootstrap hypothesis but remains diagnostic.
  The paper all-row consistent-z0 conditioning audit records 6 one-step rows,
  max residual 7.03e-12, full rank 132, max raw/equilibrated conditions
  1.58e13/5.07e4, raw-to-equilibrated reduction 3.15e8, and dominant
  near-null row/variable families
  `lower_pair_index3_weak_constraints`/`lower_pair_lambda`; it localizes the
  conditioning blocker but is not an accepted full-TFE replacement. The paper
  all-row consistent-z0 scaled-Newton diagnostic solves the same six-family
  residual with iterative row/column equilibration inside Newton, reducing the
  max condition diagnostic from 1.58e13 to 5.13e4 with raw-to-scaled reduction
  3.80e8 and scaled-vs-raw terminal position/velocity deltas
  1.21e-14/2.72e-13, but it leaves smooth/sharp orders at 4.046/4.420 and
  2.554/1.918, so scaling is diagnostic rather than an accepted replacement.
  The paper family-ablation diagnostic solves 12 one-step rows over two
  five-family variants, keeps full rank 132 with max residual 7.286e-12,
  records max raw/scaled conditions 1.58e13/1.39e5, and localizes the near-null
  family to `lower_pair_index3_weak_constraints`/`lower_pair_lambda` without
  accepting full TFE replacement. The paper lower-pair/lambda Schur diagnostic
  solves 6 one-step rows on the same six-family residual, finds a zero direct
  lower-row/lambda block and a full-rank reduced Schur block with max condition
  5.98e3, then checks the Schur-ordered Newton direction against the raw solve
  with max linear residual 1.15e-14 and max relative direction difference
  7.79e-09. It keeps `full_tfe_stage_replacement=false`. The paper lower-pair
  row-variant diagnostic compares position-, velocity-, and acceleration-level
  lower-pair row formulas over 18 one-step rows inside the same six-family
  residual. All variants solve with full rank 132 and max residual 7.286e-12;
  `acceleration_constraint` is the best Schur-conditioned variant with max
  Schur condition 9.71e1 versus the position baseline max 5.98e3, while still
  keeping `full_tfe_stage_replacement=false`. The paper lower-pair acceleration
  terminal-output h-sweep diagnostic advances that best-conditioned acceleration
  row to 6 smooth/sharp full-trajectory rows, solves all 6 row families and 132
  stage rows with max terminal residual 8.35e-12, full rank 132, max raw/scaled
  conditions 4.37e8/5.83e3, smooth position/velocity orders 4.937/4.799, and
  sharp position/velocity orders 2.555/1.918, but keeps
  `accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.
  The paired paper lower-pair acceleration projection-dependence audit compares
  raw terminal paper output with endpoint-velocity-projected terminal output
  over those same 6 rows, records raw/projected endpoint velocity residuals
  7.99e-06/9.66e-15, max projection delta 7.92e-06, and 6/6 rows requiring
  projection, so the projection-free full-TFE blocker remains explicit.
  The paper lower-pair acceleration terminal-velocity closure diagnostic then
  replaces only the final lower-pair acceleration rows with 8 weighted raw
  terminal endpoint-velocity rows, closes raw terminal velocity to 5.80e-16
  without output projection, records max closure residual 9.73e-12, rank 132,
  max raw/scaled conditions 1.28e10/7.99e4, smooth/sharp orders 3.459/4.838
  and 2.555/1.918, and keeps `full_tfe_stage_replacement=false` because those
  terminal rows are replaced rather than derived from an independent full-TFE
  stage functional.
  The paper lower-pair acceleration terminal-row homotopy audit solves 30
  one-step rows over beta=[0,0.25,0.5,0.75,1], records max residual 6.22e-12,
  full rank 132, raw/scaled max conditions 1.28e10/7.86e4, and beta0/beta1
  terminal velocity residuals 2.34e-10/1.29e-12 while keeping
  `full_tfe_stage_replacement=false`.
  The paper lower-pair terminal source-target audit records 6 case/h rows,
  maps the 8 replaced terminal rows to 24 candidate stage-local lower-pair
  source rows over the three paper stages, and keeps
  `terminal_row_replacement_present=true` and
  `full_tfe_stage_replacement=false`.
  The paper lower-pair terminal source-lift audit records 6 case/h rows, lifts
  that source into 24 stage-local lower-pair rows by
  `sqrt(h*b_i)*terminal_lower_pair_source`, and records max lift reconstruction
  error 0.0 plus max lift-ratio deviation 2.22e-16 while still keeping
  `full_tfe_stage_replacement=false`.
  The paper lower-pair terminal source-normalization audit records 6 case/h
  rows, shows the raw budget source has max terminal reconstruction relative
  error 9.47e-1, and verifies
  `terminal_lower_pair_source = terminal_row_vector/sqrt(h*b_terminal)` with
  zero normalized reconstruction error while still keeping
  `substituted_into_newton_residual=false` and `full_tfe_stage_replacement=false`.
  The follow-up terminal source-insertion audit records 12 sign/case/h rows,
  inserts the normalized source into the lower-pair Newton residual, converges
  all 12 one-step attempts, selects source_sign=-1, and records residuals from
  4.00e-13 to 9.77e-12 while still keeping
  `accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.
  The terminal source-insertion trajectory audit then runs that best sign over
  h=[0.04,0.02,0.01], completes all 6 smooth/sharp trajectory rows and all 28
  source-ready/source-insertion steps with max source-insertion residual
  9.75e-12, but the h=0.005 reference fails and raw terminal endpoint velocity
  reaches 7.41. It is a quantified failure frontier rather than an accepted
  h-sweep or full-TFE stage replacement.
  The terminal source-insertion blow-up audit records 14 case/metric rows and
  12 blow-up signals, with max mid-to-fine/coarse-to-fine ratios
  7.339e3/4.936e5, minimum observed h-power -9.456, and dominant signal
  `cylindrical_smooth:max_normalized_source_norm`. It localizes the blocker to
  a refinement-unstable closure-derived source policy while keeping
  `accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.
  The bounded-policy audit records the corresponding bounded-source target,
  rejects the closure-derived source metrics, and shows that simple extra h^2
  scaling is still insufficient for the dominant rows. It keeps
  `accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.
  The stage-local bounded-source formula audit records 6 smooth/sharp case/h
  rows and separates one-step source scaling from recurrence: the local
  `source_i = sqrt(h*b_i)*(terminal_lower_pair_row/sqrt(h*b_terminal))`
  formula is bounded with minimum local h-power 0.426, but the recurrent
  terminal-closure source remains unbounded with minimum h-power -9.456, max
  recurrent/local source ratio 1.003e6, and max raw terminal velocity 7.41.
  The paper lower-pair direct endpoint-velocity source audit removes the
  rejected recurrent terminal-closure source generator from the source path by
  taking the raw endpoint velocity residual `C_v` from the paper acceleration
  predictor's raw terminal Lobatto node and inserting `sqrt(h*b_i)*C_v` into the
  lower-pair stage blocks. Its 6 smooth/sharp trajectory rows over
  h=[0.04,0.02,0.01] against h=0.005 give minimum position/velocity orders
  2.555/1.918, minimum direct-source/terminal-velocity h-powers 0.307/0.286,
  max direct source 8.118e-6, and max post-insertion terminal velocity
  7.969e-6, with terminal-closure source and terminal-row replacement source
  both false. It remains partial because the source is still
  endpoint-boundary-derived and not the final independent paper TFE stage
  residual.
  The paper lower-pair direct-source residual-substitution audit evaluates the
  raw paper acceleration lower-pair rows at the source-inserted solution and
  verifies `raw_lower_pair + sqrt(h*b_i)*C_v = 0` over 6 smooth/sharp
  trajectory rows. Max balance and inserted lower-pair residuals are
  1.821e-13, all 28 source-residual-substituted steps are clean, and the
  h-sweep retains minimum position/velocity orders 2.555/1.918. It is still
  partial because the source remains endpoint-boundary-derived and
  `full_tfe_stage_replacement=false`.
  The residual-derived stage-source audit reconstructs
  `C_hat_i=-R_i/(source_sign*sqrt(h*b_i))` from the raw lower-pair residual
  rows, records 6 trajectory rows, max derived-vs-direct source gap 1.289e-12,
  max stage-consistency gap 1.406e-14, max mean reconstruction error
  1.482e-15, zero derived balance error, and all 28 residual-derived
  consistency steps clean while preserving the same 2.555/1.918 minimum
  position/velocity orders. It is still partial because the trajectory source
  remains direct endpoint data and `full_tfe_stage_replacement=false`.
  The self-consistent endpoint-source audit computes `C_v(x_terminal)` inside
  the lower-pair Newton residual rather than passing an external endpoint
  source. It records 6 trajectory rows, max residual/balance/source
  9.441e-12/1.821e-13/7.974e-06, smooth/sharp orders 5.333/6.790 and
  2.555/1.918, and all source steps clean while keeping the source
  endpoint-boundary-derived and `full_tfe_stage_replacement=false`.
  The paper lower-pair source-free elimination rank audit records 6 trajectory
  rows, reconstructs stage-consistent `C_hat_i` with max consistency gap
  1.406e-14, and shows the source-free centering/elimination map has rank 16
  for 24 lower-pair stage rows. The remaining 8-row rank defect is the missing
  mean-source closure budget, so full TFE still needs 8 independent lower-pair
  mean-source rows from the paper stage functional.
  The paper residual-substitution contract
  audit maps six row-family targets with 6 formulas, 6 substituted rows, 0
  accepted h-sweep rows, and `full_tfe_stage_replacement=false`.
  The stage-probe block-order audit records 12 block/case rows with max gap
  7.744e-11 and gap-order range 3.918/7.384, keeping it as scaling evidence for
  the missing weak/TFE rows rather than a solved residual.
  The stage-probe boundary-source audit records 36 block/h rows and reconstructs
  every evaluated probe block from endpoint-boundary source seeds lifted by
  sqrt(h*b_i), with max lift error 0.000e+00 and max lift-ratio deviation
  2.220e-16; this verifies the current probe source without claiming a derived
  full-TFE weak stage functional.
  The stage-probe source-budget audit compresses those rows into 6 case/h
  budgets, verifies the aggregate lifted L2 ratio to 3.331e-16, and identifies
  `newton_euler_weak_balance` as the dominant source family in both smooth and
  sharp cases.
  The stage-probe beta homotopy solves 30 one-step rows over h=[0.04,0.02,0.01]
  and beta=[0,0.25,0.5,0.75,1], with max residual 4.029e-15 and max probe norm
  2.348e-11; it is continuation evidence rather than a derived full-TFE stage
  functional. The stage-probe block-activation audit solves 36 isolated block rows
  over the same h-sweep with max residual 1.696e-15 and max activated probe norm
  2.177e-11. The stage-probe component-activation audit targets the dominant
  body0 translational Newton-Euler source component with 6 isolated component
  rows, max residual 1.195e-15, max activated component probe norm 2.006e-11,
  and max lift-ratio deviation 2.220e-16. The stage-probe component-formula
  audit inserts that target as `sqrt(h*b_i)*m0*delta_v0`, solves 6 direct
  formula rows with max residual 1.258e-15, zero formula/generic component
  difference, and max lift-ratio deviation 2.220e-16 while still not claiming
  a full-TFE stage functional. The stage-probe Newton-Euler formula audit
  inserts the full 12D weak-balance source block as
  `sqrt(h*b_i)*concat_i[m_i*delta_v_i, J_i*delta_w_i]`, solves 6 direct
  block-formula rows with max residual 1.265e-15, zero formula/generic block
  difference, and max lift-ratio deviation 3.331e-16 while still not claiming
  all stage row families. The stage-probe all-source formula audit covers all six endpoint-boundary source families as direct formulas, solves 6 direct 132-row formula rows with max residual 4.029e-15, zero formula/generic stage-major and block differences, and max lift-ratio deviation 3.331e-16 while still not claiming a derived full-TFE stage functional. The stage-probe all-source trajectory bridge solves 6 complete trajectory rows over h=[0.04,0.02,0.01] against same-formula h=0.005 references with max residual 2.192e-12, max formula probe 8.383e-11, and max position/velocity reference errors 9.45e-06/2.36e-03 while still using endpoint-boundary source formulas. The full-stage acceptance gap audit records 6 case/h rows, max proxy residual 2.192e-12, max proxy probe 8.383e-11, 6 satisfied acceptance checks, and 3 missing blockers while explicitly preserving the endpoint-boundary source and derived full-TFE replacement gaps. The stage-probe coupled-budget audit records max beta1/isolated-L2
  The stage-local source-removal target audit maps all 36 verified
  endpoint-boundary source rows onto six stage-local weak-row replacement
  targets, records `newton_euler_weak_balance` as the dominant source family,
  and keeps source removal and full TFE replacement explicitly pending.
  The stage-probe coupled-budget audit records max beta1/isolated-L2
  deviation 1.480e-02 and max solved/beta1 probe ratio 1.292e+02, keeping it
  as block-coupling evidence rather than the derived full-TFE stage functional.
  The stage-probe trajectory-accumulation audit records max solved/beta1 ratio
  1.292e+02 and max per-step ratio 1.615e+01, quantifying trajectory-level
  accumulation without claiming a full-TFE replacement.
  The stage-probe beta-trajectory bridge solves 18 full-trajectory rows over
  beta=[0,0.5,1] and h=[0.04,0.02,0.01] against same-beta h=0.005 references,
  with max residual 2.192e-12 and max probe norm 8.383e-11; it is
  trajectory-level bridge evidence rather than the derived full-TFE stage
  functional.
  The lower-pair source-free mean-velocity closure candidate supplies the
  rank audit's missing 8 rows as paper-stage mean-velocity closure rows. It
  solves 6 smooth/sharp h-sweep rows with max residual 8.13e-12 and no endpoint
  source, terminal-row replacement, or projection, but smooth/sharp orders
  3.512/4.448 and 2.555/1.918 keep `full_tfe_stage_replacement=false`.
  The source-free mean-blend closure audit sweeps 7 alpha values over 42
  one-step rows, keeps endpoint source, terminal-row replacement, and
  projection removed, and finds best alpha 0 with max residual/raw terminal
  velocity 5.489e-12/2.337e-10. It remains partial because terminal velocity is
  still above 1e-10 and no accepted trajectory h-sweep is present.
  The source-free mean-blend trajectory audit promotes that best alpha to 6
  trajectory rows, solves cleanly with max residual/raw terminal velocity
  9.453e-12/8.234e-06, and records smooth/sharp orders 5.317/6.782 and
  2.555/1.918. This falsifies the one-step near-closure at trajectory level:
  terminal velocity remains open and full=false.
  The source-free mean-blend trajectory alpha sweep tests all 7 alpha values
  over 42 trajectory rows, identifies alpha 0.75 as the best terminal-velocity
  trajectory choice, and records max residual/raw terminal velocity
  8.779e-12/7.447e-06 with minimum position/velocity orders 2.555/1.918.
  This rules out simple alpha tuning as the full-TFE repair and keeps
  terminal velocity open and full=false.
  The source-free component-blend trajectory audit tests an 8-component alpha
  vector from a one-step h=0.02 screen and records max residual/raw terminal
  velocity 9.971e-12/7.458e-06, minimum orders 2.555/1.918, and a 1.001
  terminal-velocity ratio versus the scalar alpha baseline, so per-component
  alpha tuning does not close the terminal-velocity blocker and full=false.
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
  residual 9.75e-12, but it keeps a terminal-boundary row, leaves endpoint
  boundary source removal false, loses the smooth-order gate with smooth orders
  3.523/4.828, and keeps `full_tfe_stage_replacement=false`.
  A lower-pair closure acceptance matrix compares 14 closure families, accepts
  0 candidates, identifies `source_free_mean_blend_trajectory_best_alpha` as the
  best source-free/order-preserving row set and
  `centered_terminal_velocity_bridge` or
  `source_free_final_stage_velocity_closure` as terminal-velocity row sets, so
  the accepted-order and terminal-closure requirements remain split instead of
  proving full TFE.
  The closure property Pareto audit groups the same 14 candidates into 5
  property-intersection rows and confirms an empty accepted intersection: 9
  candidates are source-free/no-replacement, 5 are order-preserving
  source-free, and 3 are terminal-velocity closed.
  The closure row-span audit tests the existing 40-row source-free basis
  against the 8 terminal-bridge target rows over 6 case/h local tangents:
  basis rank is 40, augmented rank is 48, max independent target rank is 8,
  max projection relative residual is 2.814e-01, and row-span reproduced count
  is 0. The missing-direction decomposition has rank 8, is orthogonal to the
  tested basis to 8.75e-16 relative, and reconstructs the terminal-bridge
  target with max reprojection residual 9.25e-14, but remains
  terminal-boundary-derived. Its column-energy structure is velocity-level:
  angular velocity is dominant in all 6 rows with max fraction 0.506,
  translation velocity reaches 0.496, lower-pair lambda is 0, and translation
  acceleration stays below 5.60e-05. This shows the current terminal-closing
  row cannot be recovered by reweighting the already-tested source-free basis,
  so the next repair needs a stage-local source-free velocity-level formula for
  the eight missing lower-pair tangent directions.
  The endpoint TFE readiness audit records 31 satisfied, 38 partial, and 1 missing check:
  independent full TFE stage replacement remains missing.
  Row-colored VJP now assembles the same 2637-entry pruned pattern
  with 60 row colors rather than 90 column colors; it preserves roundoff
  trajectory agreement. A five-repeat warmed benchmark records median
  row/column runtimes 1.008x for smooth and 0.990x for sharp, while dense
  `jacfwd` remains faster with dense/row 0.873x and 0.819x; the sparse
  speed gap audit records row-VJP speedups needed 1.145x smooth and 1.220x
  sharp to match dense. The sparse cost-model audit records that row-VJP
  runtime must drop by 12.7% smooth and 18.1% sharp to match dense, or by 21.4%
  smooth and 26.3% sharp for a 10% dense win, with dense-equivalent row colors
  52.4 smooth and 49.2 sharp. After projecting
  the initial velocity state onto the cylindrical velocity constraints, the
  dense convergence sweep gives smooth position order 7.161 and smooth velocity
  order 7.066 against the h=0.005 reference. The sharp case remains
  order-reduced, with position order 1.894 and velocity order 2.683. A
  Brown-McPhee smoothness sweep on the same
  cylindrical chain gives position/velocity orders 7.161/7.066, 6.494/5.657,
  3.392/4.511, and 1.894/2.683 at stribeck velocities 0.50, 0.20, 0.10, and
  0.05, confirming a smooth-to-sharp transition. A sharp adaptive
  step-doubling diagnostic then reduces vs=0.05 velocity error from 5.70e-05
  at fixed h=0.01 to 3.81e-07 at 3.2x runtime, with error/runtime value ratio
  0.002. The adaptive tolerance/work fit gives velocity slopes 0.881 over all
  tolerances and 1.710 over the two looser tolerances, with a finest-pair
  reference-floor flag. A sharp fixed-refinement audit over h=0.02/0.01/0.005
  against h=0.0025 gives all-point position/velocity orders 3.294/5.867 and
  tail orders 5.364/8.437, so the finest velocity error is high-order while
  position remains slightly limiting. A deeper fixed-refinement audit over
  h=0.01/0.005/0.0025 against h=0.00125 gives all-point position/velocity
  orders 6.398/5.870 and tail orders 7.423/3.177, so the position branch is
  high-order at the deeper scale but the velocity tail remains reduced. The
  ultra audit over h=0.005/0.0025/0.00125 against h=0.000625 gives all-point
  position/velocity orders 7.521/5.725 and tail orders 7.626/8.279. The sharp
  refinement cost-envelope audit uses h=0.01 as the practical baseline and
  records that the h=0.00125 high-order window costs 7.76x runtime, 8.0x
  steps, and 8.0x Newton iterations while reducing velocity error by 1.06e6x,
  so the remaining sharp-friction caveat is practical cost/coarse-regime
  reduction rather than asymptotic failure. The
  v046 ASME baseline summary is ingested
  into `cylindrical_chain_asme_gate.csv`; v047 now maps the exact ASME
  single-pendulum driven kinematics with position/velocity/acceleration orders
  6.006/6.007/6.005 and max drive residual 9.49e-11. A full absolute-coordinate
  driven single-pendulum FullVA residual now solves right-Lie orientation
  increments, COM position/velocity/acceleration, angular velocity/
  acceleration, pivot reactions, axis multipliers, and the drive multiplier;
  it gives position/velocity/orientation/omega orders 6.073/6.033/6.055/6.024
  with max stage residual 3.66e-12 and max translational/rotational residuals
  8.04e-14/2.67e-12. The embedded scalar FullVA bridge remains as a cross-check
  with position/velocity orders 6.006/6.004. Newton-Euler reaction multipliers
  are also reconstructed on the same driven trajectory with translational/
  rotational dynamics residuals 5.7e-14/2.8e-14, max pivot force 6.34e2, and
  max drive multiplier 3.18e2. It also keeps a partial
  single-pendulum method-side free-revolute run using the ASME
  geometry/mass/inertia, with orientation order 5.473 and omega order 5.883
  against h=0.005. The new double-pendulum method-side FullVA run maps the
  ASME lengths/masses/inertias and two-revolute topology into v029, giving
  orientation order 6.101 and omega order 6.089 with endpoint constraints below
  8.4e-12. The double-pendulum reference policy now accepts the nested local
  v029/FullVA h=0.005 self-reference for v047 validation. A direct v029-v046
  double-pendulum trajectory diagnostic is retained after rotating the v029
  coordinate convention into the ASME rA world frame: the finest h=0.01 pos/vel
  Linf errors against v046 h=0.001 are 1.17e-3/2.94e-5 and the observed orders
  are near zero. A reference-floor check with v046 h=0.0005 halves those errors
  with pos/vel ratios 0.500/0.497, supporting the policy that v046 rA is a
  reproducibility baseline and floor diagnostic rather than the accepted oracle.
  A four-example lower-pair constraint-graph bridge now evaluates all ASME JSON
  DP1/CD/DP2/D rows at position, velocity, and acceleration levels with
  h=[0.02,0.01,0.005]. The bridge records 18-row graph mappings for four_link
  (DP1=6, CD=12) and slider_crank (DP1=7, DP2=4, CD=6, D=1). A matching
  four-example `Phi_q` SVD rank audit verifies full row rank for all ASME
  constraint graphs over h=[0.02,0.01,0.005], with min singular values
  3.04e-1/2.03e-1/7.89e-2/7.25e-2 for single/double/four_link/slider_crank
  and max condition numbers 7.94/15.7/117/43.7. The local closed-loop
  kinematic FullVA solve now accepts four_link and slider_crank by solving
  Phi=0, Phi_q qdot=nu, and Phi_q qdd=gamma with SO(3) projection on
  h=[0.02,0.01,0.005]. The max Phi/velocity/acceleration residuals are about
  6.7e-15/3.0e-15/1.1e-14 for four_link and
  9.0e-16/4.8e-16/1.2e-15 for slider_crank. Reaction-dynamics reconstruction
  solves for multipliers on those accepted states and checks Newton-Euler rows,
  giving max full dynamics residuals 1.34e-13 for four_link and 6.49e-15 for
  slider_crank. A read-only output validator now covers the
  292 generated result files, 147 CSV tables, 120 PNG plots, summary gate status,
  stale wording, and README/report artifact lists.
- Latest lower-pair candidate frontier audit:
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_candidate_frontier_audit`
  aggregates 11 candidate families and 115 rows, with 35 terminal-closed rows,
  17 smooth-order rows, and zero order/terminal intersections; full-TFE remains
  open pending a bounded target-free stage-local weak-row tangent.
- Latest bounded tangent requirement audit:
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_bounded_tangent_requirement_audit`
  records `requirement_row_count=7`, `row_space_oracle_span_count=36`,
  `target_free_formula_span_count=0`, and
  `bounded_gradient_practical_cap_spanning_row_count=12`; this keeps the
  positive span result oracle-only and preserves the bounded target-free
  stage-local weak-row tangent as the missing full-TFE formula target.
- Latest recurrent stage2 feature-dictionary span audit:
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit`
  records `feature_dictionary_row_count=12`, `span_row_count=8`,
  `combined_all_dictionary_span_count=2`, best dictionary `stage2_matrix_core`,
  and residual `1.084e-14`, while preserving
  `formula_coefficient_law_present=false` and
  `full_tfe_stage_replacement=false`; the next target is a bounded target-free
  coefficient/selection law plus nonlinear h-sweep.
- Latest recurrent stage2 frozen coefficient-law screen:
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit`
  records `coefficient_law_row_count=60`, `span_count=0`, best dictionary
  `combined_all_target_free_dictionary`, best law `closure_delta_norm_weights`,
  and residual `5.596e-01`, while preserving
  `coefficient_derivative_included=false`,
  `target_jacobian_used_for_formula=false`, and
  `full_tfe_stage_replacement=false`; the next target is state-dependent
  bounded coefficients with derivative terms plus nonlinear h-sweep.
- Latest recurrent stage2 state-feature coefficient-derivative screen:
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit`
  records `state_feature_coefficient_derivative_row_count=36`,
  `span_count=0`, best dictionary `stage2_matrix_core`, best law
  `inverse_closure_delta_norm_weights_derivative`, and residual `5.908e-01`;
  it includes target-free coefficient derivative terms from candidate/recurrent
  row Jacobians, uses no target Jacobian or target direction, and preserves
  `full_tfe_stage_replacement=false`.
- Latest full-TFE blocker localization: the velocity-basis span audit tests
  7 weighted eight-row stage-velocity closure families plus the 24-row all-stage
  velocity upper bound against the 8 terminal-bridge tangent rows. The all-stage
  velocity rows span at max relative residual 2.78e-15, but the best weighted
  candidate is `endpoint_lagrange_velocity_closure` at 4.20e-01 and no weighted
  candidate spans, so full TFE still needs an eight-row source-free compression
  followed by a nonlinear trajectory h-sweep. The h-adaptive endpoint-pose
  velocity response audit records four law-response rows with
  `terminal_closed_row_count=1`, `smooth_order_ok_count=0`, and no accepted
  order/terminal intersection, so terminal closure still requires order
  collapse rather than providing a full-TFE replacement.
- Latest velocity-compression localization: the follow-up audit fits that
  source-free eight-row compression directly in the local tangent space. All 3
  fixed candidates span all 6 smooth/sharp case/h samples at roundoff; the best
  fixed candidate is `optimized_global_stage_scalar` with weights numerically
  `[0,0,1]`, selecting the final paper-stage lower-pair velocity rows, and
  best relative residual 1.04e-15. The strengthened selector-degeneracy check
  shows all fixed fits collapse to that final-stage selector: universal full
  8x24 selector distance is 1.53e-15 and max non-final-stage energy fraction is
  1.71e-15. The non-degenerate follow-up sweeps 192 fixed stage-0/stage-1
  injection rows; 84 rows have meaningful non-final-stage energy, but none
  spans locally and the best meaningful projection residual is 1.59e-03. The
  state-local diagonal direction oracle then sweeps 72 rows over 65 direction
  samples; 36 rows have meaningful non-final-stage energy, but none spans
  locally and the best meaningful projection residual is 9.90e-03. The
  non-final full component-mixing follow-up tests 36 stage-0/stage-1/stage-0+1
  full-mixing rows; 0 span locally and the best tangent residual is 9.81e-01.
  The value-level source-free probe then tests 72 case/h/candidate rows; all 72
  balance row values, 18 are value-balanced local tangent spans, but 0
  meaningful non-final value-balanced rows span. The successful spans are
  final-stage-selector-like with max spanning non-final-stage energy fraction
  2.12e-15. The derivative-aware local oracle then tests 36 non-final rows;
  all 36 balance values and span locally with meaningful non-final energy
  after a coefficient-gradient correction. The bounded-gradient cap sweep then
  tests 288 cap/candidate/case/h rows; all 288 keep value balance and
  meaningful non-final energy, 92 span at the tested caps, practical cap 1e12
  spans 12 rows, and all 36 local spans require cap 1e18. This is still an
  oracle rather than a bounded analytic row formula, so
  `full_tfe_stage_replacement=false` remains.
- Latest bounded-formula velocity-compression localization: the bounded
  analytic saturation-law probe tests 648 law/cap/candidate/case/h rows over
  global tanh, rowwise tanh, and rowwise rational-quadratic laws. All 648 rows
  keep value balance and meaningful non-final energy, 366 span at the tested
  caps, and all local spans require cap 1e22 for every tested law. The
  correction direction is still a target-direction oracle and no nonlinear
  h-sweep is accepted, so `full_tfe_stage_replacement=false` remains.
- Latest target-free velocity-compression localization: the target-direction-free
  bounded formula probe tests 2592 law/cap/candidate/case/h rows over negative
  closure, closure, mean active velocity, dominant active velocity, stage-2
  extrapolated velocity, endpoint-extrapolated velocity, non-final stage
  slope, extrapolated-stage2-minus-closure, all-active mean, all-active
  anti-aligned row, all-active SVD modes, and closure-orthogonal all-active SVD
  direction laws. All 2592 rows
  keep value balance and meaningful non-final
  energy, but 0 span at any tested cap; best residual is 9.82e-01. The formula
  construction does not use the target Jacobian or target direction. The
  direction-capacity follow-up tests 216 candidate/feature/case/h rows and
  shows that all-stage velocity features span 72 rows at roundoff, while every
  non-final active/source feature family has 0 spans; the best non-final
  residual is 9.81e-01 and the best non-final correction residual is 9.998e-01.
  The nonlinear second-differential capacity follow-up tests 216 rows across
  six finite-difference source-feature families; all six families have 0 spans,
  with best projection residual 6.95e-01 and best correction residual 7.01e-01.
  The higher-order/nonlocal capacity follow-up tests 216 rows over
  third-differential source features and same-case cross-step source deltas;
  all six families again have 0 spans, with the same best residuals. The
  one-step history-transport capacity follow-up tests 216 rows over transported
  source-row and non-final velocity-row deltas; all six families again have
  0 spans, with best projection/correction residuals 7.13e-01/7.12e-01. The
  two-step history-transport capacity follow-up tests 216 rows over two future
  transported source/velocity deltas; all six families again have 0 spans, with
  best projection/correction residuals 6.95e-01/7.01e-01. The recurrent
  history-capacity follow-up tests 216 rows over two-step curvature and
  bilinear source/velocity history features; all six families again have
  0 spans, with best projection/correction residuals 6.95e-01/7.01e-01. The
  weak-row structure-capacity follow-up tests 216 rows over source/active
  cross-Gram, Hadamard, cross-Hadamard, and shifted-commutator source-active
  feature families; all six families again have 0 spans, with best
  projection/correction residuals 6.95e-01/7.01e-01. The row-space compression
  follow-up tests 36 rows over target-free SVD, row-norm, and stage-balanced
  frozen eight-row velocity-space compressions; all six laws again have
  0 spans, with best projection residual 7.38e-01 and best non-final residual
  9.82e-01. The row-space coefficient-derivative follow-up then tests the
  same 36 laws/case/h rows with a target-direction derivative oracle: all 36
  local tangents span and 24 are value-balanced, with best residual 8.92e-16,
  but the required coefficient-gradient norm reaches 6.78e18. The remaining
  target-free state-feature coefficient-derivative screen then tests three
  bounded closure-norm coefficient laws over six dictionaries and 36 rows; it
  includes the derivative term, uses no target Jacobian or target direction,
  records zero spans, and reaches best residual 5.908e-01 with
  `inverse_closure_delta_norm_weights_derivative`. The remaining
  blocker is therefore a bounded target-free coefficient-gradient formula,
  expressed as a revised analytical weak-row formula or richer nonlinear
  recurrent history source law, plus nonlinear h-sweep evidence.
- Latest target-free active-velocity matrix localization: the expanded
  active-law grid tests 20 local rows and reaches best projection residual
  0.576548 with `stage2_velocity_shifted_column_broadcast_feature`, but
  independent target rank remains 8 and `any_candidate_spans_terminal_bridge=false`.
  This improves localization of the missing stage-2 velocity tangent without
  changing `full_tfe_stage_replacement=false`.
- Best-law missing-direction localization: a JSON-only two-row rerun keeps the
  best residual 0.576548 and rank-eight missing direction, but localizes the
  best remaining gap to stage 2 with dominant variable family
  `angular_velocity_w`, fraction 0.502991, and stage-2 fraction 0.963038.
- Stage-2 angular-velocity mask exclusion: an 8-row angular-only matrix grid
  runs in 35.3 seconds. Its best law
  `stage2_angular_velocity_shifted_column_broadcast_feature` reaches only
  residual 0.752997 with independent target rank 8 and no terminal-bridge
  span, shifting the remaining direction back to dominant
  `translation_velocity_v`; simple angular masking is ruled out while
  `full_tfe_stage_replacement=false` remains.
- Translation/angular cross-coupling exclusion: an 8-row target-free outer-cross
  matrix grid runs in 35.3 seconds. Its best law
  `stage2_velocity_angular_to_translation_cross_feature` reaches only residual
  0.898812 with independent target rank 8 and no terminal-bridge span; the
  remaining direction is still dominated by `translation_velocity_v` at
  fraction 0.556004 with stage-2 fraction 0.999994, so simple
  translation/angular outer-cross coefficient-gradient rows are ruled out.
- Endpoint-pose velocity-predictor localization: a 10-row target-free
  predictor grid runs in 31.2 seconds. Its best law
  `paper_endpoint_pose_positive_lagrange_z` improves the projection residual
  to 0.117782 but still has independent target rank 8 and no terminal-bridge
  span; the remaining direction is dominated by `translation_velocity_v` at
  fraction 0.514237 with stage fractions 0.961546/0.004167/0.034287.
- Near-terminal predictor degeneracy: a 14-row stage-0/stage-2 convex screen
  runs in 31.7 seconds. The stage-2-only law
  `paper_endpoint_pose_stage02_convex_0p00_z` spans locally at roundoff but is
  terminal-bridge equivalent; the best nonterminal law
  `paper_endpoint_pose_stage02_convex_0p05_z` reaches residual 0.049317 with
  independent target rank 8, `nonterminal_span_row_count=0`, and no
  nonterminal terminal-bridge span. Focused h-scaling reruns at h=0.02 and
  h=0.01 keep the nonterminal residual at 0.051890 and 0.052472, confirming a
  persistent nonterminal weak-row gap.
- Synchronized pose/velocity near-terminal row: a 10-row local audit runs in
  29.7 seconds. The best law `stage02_convex_pose_velocity_0p01_z` reaches
  residual 0.009512, with h=0.02/h=0.01 residuals 0.009978/0.010085, but keeps
  rank 8 and no nonterminal span; offsets 0p02/0p05/0p10 give
  0.019205/0.049390/0.103464, so this is localization evidence only.
- Synchronized pose/velocity terminal-limit extrapolation: the
  `0p01/0p02` law reaches residual 4.699e-06 at h=0.04, then 2.335e-06 and
  1.168e-06 at h=0.02/h=0.01, but it remains no-span and is marked
  terminal-bridge-equivalent, not independent full TFE.
- Mean-acceleration bridge correction exclusion: signed `-1/+1` corrections
  to the terminal-limit extrapolation worsen the best residual to 0.076159 or
  above and shift the gap to `lie_position_u`, so the existing acceleration
  bridge term is not the missing row.
- Bilinear active-velocity outer-product exclusion: a 24-row target-free
  feature/stage-2-velocity matrix grid runs in 57.3 seconds. Its best law
  `stage2_velocity_feature_outer_stage2_velocity` reaches only residual
  0.898720 with independent target rank 8 and no terminal-bridge span, so the
  tested component-pair coupling family is also ruled out while
  `full_tfe_stage_replacement=false` remains.
- Componentwise active-velocity diagonal exclusion: another 24-row target-free
  Hadamard/shifted-diagonal matrix grid runs in 56.7 seconds. Its best law
  `stage2_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity` reaches
  only residual 0.898530 with independent target rank 8 and no terminal-bridge
  span, ruling out the tested row-local componentwise coupling family.
- Latest final-stage velocity-closure localization: the nonlinear source-free
  audit inserts 16 centered acceleration source-consistency rows plus 8 final
  paper-stage velocity rows and solves 6 smooth/sharp trajectory rows with max
  residual 9.49e-12 and raw terminal endpoint velocity 4.01e-16, without
  endpoint source, terminal-row replacement, or projection. Smooth/sharp orders
  are 3.523/4.828 and 2.555/1.918, so terminal velocity is closed but smooth
  position order still keeps `full_tfe_stage_replacement=false`.
- Latest order/closure blend localization: the source-free trajectory audit
  tests beta=[0,0.5,1] over 18 rows. Beta 1 closes raw terminal velocity to
  4.01e-16 but keeps smooth position order at 3.523, while beta 0 and 0.5 keep
  smooth position order above 5 but leave terminal velocity around 4e-6.
  Therefore `order_and_terminal_intersection_present=false`, and the full-TFE
  blocker remains an independent eight-row source-free closure formula.
- Latest nonlinear-history source-law exclusion: the recurrent nonlinear
  history screen tests five target-free norm, Hadamard, bilinear, and
  second-difference history laws. All rows converge at rank 132 with no
  endpoint source, target Jacobian, terminal-row replacement, or projection,
  but `terminal_closed_row_count=0` and `smooth_order_ok_count=0`; the best law
  `recurrent_nonlinearhistory_velocity_terminal_source0historyhadamard_z` has
  terminal velocity 1.954e-07 and min order 3.525, so
  `full_tfe_stage_replacement=false` remains.
- Role: current in-progress cylindrical lower-pair scaffold under the new
  pipeline gate.
- Limitation: row-VJP reduces the sparse seed count and now has a cost-model
  target for the dense gap, but remains slower than dense `jacfwd`; the endpoint velocity closure is now
  represented by an endpoint KKT residual but not yet by a fully TFE-style
  endpoint treatment. Sharp-friction convergence remains order-reduced, and
  the remaining caveats are sparse speed, full TFE stage replacement,
  and practical coarse-regime sharp-friction cost rather than missing ASME rows.

### v048_cross_paper_same_test_benchmarks

- Improvement: added an executable cross-paper same-test benchmark layer that
  turns the original TFE paper plus the Kissel/Negrut-related public-code
  families into a machine-readable run plan and public-code runner.
- Evidence: [v048_report.md](v048_cross_paper_same_test_benchmarks/results/v048_report.md) and
  [validate_v048_outputs.py](v048_cross_paper_same_test_benchmarks/validate_v048_outputs.py);
  the four-example performance ledger is
  [four_example_performance_matrix.csv](v048_cross_paper_same_test_benchmarks/results/four_example_performance_matrix.csv)
  checked by
  [validate_four_example_performance_matrix.py](v048_cross_paper_same_test_benchmarks/validate_four_example_performance_matrix.py);
  the coarse-first external readiness gate is
  [coarse_first_external_readiness_gate.csv](v048_cross_paper_same_test_benchmarks/results/coarse_first_external_readiness_gate.csv)
  checked by
  [validate_coarse_first_external_readiness_gate.py](v048_cross_paper_same_test_benchmarks/validate_coarse_first_external_readiness_gate.py);
  the closed-loop surrogate dynamic gate is
  [closed_loop_surrogate_dynamic_gate.csv](v048_cross_paper_same_test_benchmarks/results/closed_loop_surrogate_dynamic_gate.csv)
  checked by
  [validate_closed_loop_surrogate_dynamic_gate.py](v048_cross_paper_same_test_benchmarks/validate_closed_loop_surrogate_dynamic_gate.py);
  the closed-loop dynamic error floor audit is
  [closed_loop_dynamic_error_floor_audit.csv](v048_cross_paper_same_test_benchmarks/results/closed_loop_dynamic_error_floor_audit.csv)
  checked by
  [validate_closed_loop_dynamic_error_floor_audit.py](v048_cross_paper_same_test_benchmarks/validate_closed_loop_dynamic_error_floor_audit.py);
  the closed-loop coarse dynamic-order probe is
  [closed_loop_coarse_dynamic_order_probe_work_precision_summary.csv](v048_cross_paper_same_test_benchmarks/results/closed_loop_coarse_dynamic_order_probe_work_precision_summary.csv)
  checked by
  [validate_closed_loop_coarse_dynamic_order_probe.py](v048_cross_paper_same_test_benchmarks/validate_closed_loop_coarse_dynamic_order_probe.py);
  the velocity-partitioning code-path audit is
  [velocity_partitioning_code_search.csv](v048_cross_paper_same_test_benchmarks/results/velocity_partitioning_code_search.csv).
- Key metric: the run plan has 17 case-inventory rows; the workload estimate
  records and the harness executes 326700 public-code steps for the full 2021
  `rA/rp/reps` public order policy. All 9/9 public step-size trio groups
  `h=[1e-2,1e-3,1e-4]`, `T=3`, across `single_pendulum`, `four_link`, and
  `slider_crank` complete as 27/27 ok rows. The selected `Gauss6/FullVA` same-mechanism pilot completes
  3/3 single-pendulum rows at `T=0.2`, `h=[0.2,0.1,0.05]`, with
  position/velocity/orientation/omega observed orders
  `6.073/6.033/6.055/6.024`. v048 also completes the 3/3 exact
  public-horizon single-pendulum `Gauss6/FullVA` step-size trio at `T=3`,
  `h=[1e-2,1e-3,1e-4]`; the finest row has position/velocity errors
  `2.584e-14/7.012e-15`, 30000 Newton iterations, and runtime `76.625s`.
  These final-error orders are roundoff/reference-floor limited and are not
  interpreted as a standalone method-order claim. v048 also completes 6/6 selected
  closed-loop `Gauss6/FullVA` rows on the 2021 `four_link` and
  `slider_crank` mechanisms at `T=0.2`, `h=[0.02,0.01,0.005]`, reference
  `h=0.001`; these rows verify constraint, SO(3), and Newton-Euler reaction
  residuals, with max dynamics residuals `1.338e-13` and `6.492e-15`, but
  are not dynamic order/work rows. The public-horizon closed-loop tranche now
  completes 6/6 rows for those two mechanisms at `T=3`,
  `h=[1e-2,1e-3,1e-4]`; the finest `h=1e-4` rows have max dynamics residuals
  `5.136e-13/1.113e-14`, runtimes `73.25s/89.49s`, and are generated through
  independent shard/merge entry points that can run in parallel. The
  public-horizon double-pendulum `Gauss6/FullVA` coarse tranche now completes
  3/3 rows at `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`, with
  position/velocity orders `7.951/7.042` and max endpoint residuals
  `1.131e-05/3.533e-04`; this is coarse-first evidence and explicitly not the
  public `1e-4` policy. The matching coarse same-window public
  double-pendulum baseline artifact now records `rA/reps` as 6/6 ok rows with
  position/velocity orders `0.703/0.754`, while `rp` records three Newton
  nonconvergence rows. The single-pendulum coarse same-window tranche records
  9/9 public rows, 3/3 local rows, a 4-row work/precision summary, and local
  position order `6.054` under the same no-default-`1e-4` coarse policy. The
  2-row closed-loop surrogate dynamic gate records
  selected-window residual-to-error evidence for `four_link` and
  `slider_crank`, with `accepted_dynamic_order_count=0`, so it does not close
  the dynamic order/work gap. The 2-row closed-loop dynamic error floor audit
  records velocity/acceleration floor evidence for both mechanisms, two
  position/reference-floor blockers, and `accepted_dynamic_order_count=0`. The
  closed-loop coarse dynamic-order probe records `11/12` ok rows at `T=0.2`,
  `h=[0.1,0.05,0.025]`, reference `h=0.0125`, one public
  `slider_crank`/`rA` failure at `h=0.1`, local velocity/acceleration
  evidence for both mechanisms, two local position-floor rows, and
  `accepted_dynamic_order_count=0`; larger steps therefore do not close the
  four-link/slider-crank dynamic-order gap. The
  public `double_pendulum` dynamic self-reference order artifact now completes
  9/9 rows for `rA/rp/reps` at `T=3`, `h=[1e-2,2e-3,1e-3]`, reference
  `h=1e-4`. The public timing/iteration artifact now completes 12/12 rows
  for `rA/rp/reps` on all four examples at `T=3`, `h=1e-3`, generated through
  shard/merge entry points. The coarse-first external readiness gate records
  four example rows, `coarse_first_ready_examples=2/4`,
  `closed_loop_surrogate_available=2`, `closed_loop_floor_audit_available=2`, and
  `coarse_first_dynamic_order_missing=0`, so the no-default-`1e-4` policy and
  coarse/read-only closed-loop dynamic-order coverage are validated directly
  without creating an external-superiority claim. The
  four-example performance matrix records 48 method/example rows, 32 completed
  rows, and 0 partial rows while keeping `external_superiority_claim=false`.
  A bounded 2022 half-implicit
  four-example pilot now completes 24/24 rows and 8/8 `rA/rA_half`
  model-form trios at `T=0.1`, `h=[0.02,0.01,0.005]`; this is runner
  evidence rather than accepted full-2022 `T=8` convergence. The
  velocity-partitioning code-path search has 11 audit rows, records the
  EasyChair PDF reference check and public web-search status, checks both
  `sbel-reproducibility` and `public-metadata` refs `origin/master` plus
  `origin/user/aaron/msd`, finds 0 exact velocity-partitioning path hits, and
  rejects 2024 `MNODE-code` mechanism-name hits as a different code path.
- Role: external-comparison scaffold for the CMAME same-test gate.
- Limitation: this is not a new integrator and not superiority evidence;
  `same_test_campaign_status=not_run`, `external_superiority_claim=false`, and
  the 2022/TFE/velocity-partitioning campaigns plus remaining
  `Gauss6/FullVA` external rows are still open.

## Plot

Regenerate the progression plot with:

```bash
.venv_sbel/bin/python plot_version_ledger.py
```

Output:

```text
version_progression.png
```
