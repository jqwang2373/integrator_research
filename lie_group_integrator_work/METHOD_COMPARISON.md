# Why The Current Path Is Better, And Where That Claim Stops

This file records the argument against the nearby paper baselines. It is based
on the local v001-v045 experiments, not on a production multibody benchmark.
The per-version mathematical order proof/status record is
`ORDER_PROOF_LEDGER.md`.

## Current Best Local Recipe

For the frictional constrained rigid-body cases tested here, the strongest
recipe is:

```text
unit quaternion S^3 residual
+ JAX/AD Newton Jacobian through friction and Lagrange multipliers
+ Gauss6 collocation when the friction law is smooth
+ embedded Gauss64 adaptivity near sharp friction transitions
+ PivotVA stage velocity/acceleration constraints for the full revolute DAE
+ FullVA as an off-axis constrained-torque stress check
+ double-revolute interbody stress testing
+ sparse/block Newton linear algebra for scaling the full DAE residual
+ batched colored sparse AD for avoiding dense Jacobian materialization
+ block-symbolic sparsity for avoiding dense warm-up pattern discovery
+ JVP-pruned sparse pattern discovery for recovering the fine pattern without dense Jacobians
+ cached sparse pattern reuse across friction regimes
+ triple-revolute larger-topology validation
+ generated block-dependency pattern acquisition for the triple-revolute residual
+ generated-block cache refresh/union for longer and perturbed triple-revolute runs
+ skew-axis parent-child revolute constraints for non-coplanar lower-pair geometry
+ skew-axis prismatic lower-pair coverage for a non-revolute sliding joint
+ double-prismatic interbody lower-pair coverage for parent-child sliding coupling
+ row-colored VJP diagnostic for reducing prismatic sparse-AD seed count
```

The best full absolute-coordinate revolute result is now v027 PivotVA. In the
Brown-McPhee h=0.0125 tests, Gauss6 PivotVA reduces endpoint velocity drift to
5.213e-13 in the smooth case and 1.570e-12 in the sharp case, while enforcing
stage pivot acceleration at about 1e-15.

v028 adds an off-axis torque and explicit hinge-axis velocity/acceleration
constraints. It tightens axis diagnostics to about 1e-25, but does not change
the one-DOF trajectory relative to PivotVA. That makes it a useful stress check,
not a new trajectory winner.

v029 moves from one body to a two-body double-revolute chain. PivotVA reduces
Gauss6 endpoint velocity drift from 1e-4 scale to 1e-11--1e-12 scale at the
interbody topology. That makes the repair less likely to be a one-body artifact,
but it also exposes the dense Newton cost problem.

v030 diagnoses that cost problem. The Gauss6 double-revolute FullVA Newton
Jacobians are 138 by 138 but only about 3% dense. In the recorded first-step
systems, CSR `spsolve` is orders faster than dense linear solve for Gauss6, so
the next implementation target is sparse/block Newton rather than another small
change to the one-joint equations.

v031 puts that sparse solve inside the time integrator. In the targeted h=0.02,
T=0.10 double-revolute tests, Gauss6 FullVA dense runtime is 3.408s versus CSR
0.109s in the smooth case and 2.838s versus 0.129s in the sharp case. Final
dense-vs-CSR orientation differences are at roundoff scale, so sparse Newton is
now an implementation improvement, not just a diagnostic.

v032 tests the next obvious solver idea: matrix-free Newton-Krylov using JAX
JVPs instead of dense Jacobian materialization. The JVP is correct to roundoff,
but unpreconditioned GMRES fails after 200 iterations on both targeted Gauss6
FullVA systems. This keeps v031 CSR sparse Newton as the best implemented path
and clarifies that matrix-free needs preconditioning or block structure.

v033 tests the other cheap solver idea: lag the sparse Jacobian in a modified
Newton loop. It preserves the trajectory to roundoff scale, but the extra
Newton corrections offset the fewer Jacobian evaluations. This keeps fresh CSR
as the best small-system implementation and narrows the next target to real
structured sparse/block assembly or preconditioned Krylov.

v034 tests that structured sparse-AD target with column coloring and JAX JVPs.
With a warm-up union sparsity pattern, it reconstructs the sparse Jacobian to
roundoff and preserves the trajectory, but it is slower than dense `jacfwd` on
the 138D system because it needs 11 JVP calls per Jacobian assembly. This turns
"use sparse AD" into a sharper implementation requirement: use hand/block
assembly, compiled/batched coloring, or a larger topology where dense Jacobian
memory/cost dominates.

v035 tests the compiled/batched coloring requirement directly. It batches the
11 colored seed vectors into one `vmap(jvp)` dispatch, keeps the same 582-entry
sparsity pattern, and matches dense Jacobian values to about 4.5e-18 relative
error. On the same h=0.02, T=0.06 double-revolute runs, batched colored JVP
runtime is 0.038s smooth and 0.035s sharp, versus dense `jacfwd` CSR at 0.102s
and 0.088s. This makes structured sparse AD a positive implementation result,
not only a correctness proof.

v036 removes the remaining dense warm-up pattern dependency. It derives a
conservative block-symbolic mask from the residual's physical block structure.
The mask is coarser than the warm-up union pattern, 1755 entries and 34 colors
versus 582 entries and 11 colors, but it misses zero dense entries and keeps
roundoff trajectory agreement. Pattern construction drops from seconds to
milliseconds. Runtime remains competitive despite the overpattern: the sharp
case is 0.050s versus dense `jacfwd` CSR at 0.079s, and the smooth case is
essentially tied.

v037 then refines the v036 superset without dense Jacobians. It runs batched
JVPs through a short Newton/trajectory dry-run inside the safe block-symbolic
mask and unions the active entries. The resulting pattern exactly matches the
dense warm-up union pattern in both smooth and sharp tests: 582 entries,
11 colors, zero extra entries, and zero missing entries. Pattern discovery is
also much cheaper in the recorded run, 0.053-0.067s versus 0.952-1.082s for
dense warm-up discovery.

v038 tests whether the v037 pattern can be cached and reused. A pattern
discovered once from the smooth short dry-run has 582 entries and 11 colors.
Reused over T=0.12, it has zero missing entries against dense validation
patterns in both smooth and sharp cases. Runtime is also better than dense
`jacfwd` CSR on the longer runs: 0.065s versus 0.097s in smooth and 0.068s
versus 0.101s in sharp.

v039 moves the sparse-AD result beyond the double-revolute benchmark. It builds
a three-body triple-revolute chain with Brown-McPhee friction at all three
hinges and a 207D Gauss6 FullVA Newton system. The JVP-pruned pattern has
930 entries and 11 colors, exactly matches dense validation in both smooth and
sharp cases, and gives 1.41x smooth plus 1.67x sharp runtime speedups versus
dense `jacfwd` CSR with roundoff trajectory agreement.

v040 removes the remaining v039 pattern-acquisition shortcut. Instead of
starting from a full matrix superset, it generates a block-dependency superset
from the triple-revolute residual structure. The generated superset has
2691 entries and 32 colors with zero dense-validation misses. Batched JVP
pruning inside it recovers the exact dense-validation pattern, 930 entries and
11 colors, and the pruned solver is 2.14x smooth and 1.78x sharp faster than
dense `jacfwd` CSR in the recorded run.

v041 turns that acquisition result into a cache policy. A 930-entry/11-color
pattern discovered once from the smooth short triple-revolute trajectory is
reused on longer smooth/sharp nominal and perturbed trajectories. The
generated-block refresh scan adds zero entries in all four natural scenarios,
and dense validation also reports zero misses. A stale-cache audit removes
23 entries by construction; the refresh scan finds and unions all 23 without
dense Jacobians, restoring the exact dense-validation pattern.

v042 changes the constraint geometry rather than only the run policy. The
interbody revolute constraints no longer align every body axis to one global
axis; each child proximal axis is aligned to the parent body's distal axis, and
the body-fixed axes are intentionally skewed. The generated block superset has
2907 entries and 32 colors with zero dense-validation misses. JVP pruning
recovers the exact 2181-entry, 31-color dense pattern, endpoint velocity is
around 1e-16, and sparse runtime is 1.94x-1.98x faster than dense `jacfwd` CSR.

v043 changes the lower-pair type. It adds a skew-axis prismatic joint with
five constraints, one free sliding coordinate, and Brown-McPhee-style sliding
friction coupled to the normal load. The generated block superset has
1026 entries and 24 colors with zero dense-validation misses. JVP pruning
recovers the exact 414-entry, 18-color dense pattern, and dense/sparse
trajectories match exactly. This is a coverage and correctness win, not a
speed win: sparse JVP assembly is slower than dense `jacfwd` on this 69D case.

v044 moves the prismatic test from a single-body slider to a two-body
parent-child chain. The second prismatic joint couples child and parent
positions, velocities, orientations, reaction forces, and sliding friction.
The 138D residual has a generated block superset with 4824 entries and
90 colors, with zero dense-validation misses. JVP pruning recovers the exact
2439-entry, 90-color dense pattern, and dense/sparse trajectories match to
roundoff. This is again a correctness/coverage win rather than a speed win:
warmed dense/sparse runtime is 0.80x smooth and 0.87x sharp because 90 colors
make sparse JVP assembly too expensive.

v045 tests whether that 90-color bottleneck is mainly a coloring issue. It
keeps the same v044 residual and exact sparse pattern but switches assembly
from column-colored JVP to row-colored VJP. Row coloring needs 54 seeds instead
of 90 and preserves the dense trajectory to roundoff. The speed result is only
modestly positive relative to column-JVP, 1.04x in the smooth case and tied in
the sharp case, and it still loses to dense `jacfwd`. The useful conclusion is
that generic coloring alone is not enough for the prismatic chain; the next
solver path needs component/block assembly or larger systems where reverse-mode
overhead amortizes.

## Compared With Chaturvedi/Sandu/Sandu 2026 TFE Paper

What the paper gets right:

- The quaternion `S^3` Lie-group formulation avoids Euler singularities and
  avoids a separate unit-quaternion normalization constraint.
- The generalized `Pi(g)=g_p T_exp + g_theta` operator is the right engineering
  bridge for nonlinear friction/load Jacobians.
- The TFE framing is a serious attempt to handle index-3 DAE constraints at
  higher order.

Where the local path is better in current evidence:

- v010/v011 replace finite-difference Jacobian work with AD/JAX and verify the
  same transport idea to roundoff, which is the practical implementation route
  the paper motivates but does not demonstrate as its main numerical backend.
- v013-v014 show near-sixth-order smooth-friction behavior and large error
  reductions at roughly similar cost; the paper reports visible order reduction
  in its DAE/TFE experiments.
- v015/v020/v021/v022 show that sharp friction should be handled by embedded
  adaptivity, not only by increasing fixed polynomial degree.
- v027 gives a concrete non-projection full revolute DAE repair: velocity drift
  is around 1e-12 for Gauss6 PivotVA, while v023 raw Gauss6 was around 1e-3.
- v028 shows the hinge-axis part can also be enforced explicitly under off-axis
  constrained torque, but the trajectory bottleneck in the single revolute test
  remains the pivot velocity/acceleration repair.
- v029 shows the same PivotVA idea transfers to an interbody revolute joint,
  reducing endpoint velocity drift by about seven to eight orders versus raw
  Gauss6 in the double-revolute benchmark.
- v030 adds solver evidence: the successful double-revolute Gauss6 residual is
  sparse enough that dense Newton linear algebra is the wrong scaling path.
- v031 turns that evidence into a working sparse Newton loop, cutting targeted
  Gauss6 FullVA runtime by 22x-31x without changing the trajectory.
- v032 rules out plain unpreconditioned JVP-GMRES as a replacement for dense
  Jacobian materialization, narrowing the next solver target to preconditioned
  Krylov or structured sparse/block assembly.
- v033 rules out simple modified Newton/Jacobian lagging as the main scaling
  fix for the current double-revolute system.
- v034 shows sparse AD via coloring is correct, but generic Python-level
  coloring is not yet faster than dense `jacfwd` on the current 138D system.
- v035 shows compiled/batched colored sparse AD is faster than dense `jacfwd`
  on that same 138D system while retaining roundoff-level Jacobian agreement.
- v036 shows dense warm-up pattern discovery is not required for correctness:
  a block-symbolic sparsity pattern is conservative, fast to build, and still
  competitive on the targeted double-revolute test.
- v037 shows the fine warm-up pattern can be recovered without dense
  Jacobians, using the block-symbolic mask plus batched JVP pruning.
- v038 shows the recovered pattern can be cached and reused across the smooth
  and sharp friction regimes tested here, with zero longer-horizon validation
  misses.
- v039 shows the same sparse-AD direction transfers to a larger three-body
  triple-revolute topology, whereas the paper's numerical evidence is centered
  on a single revolute pendulum.
- v040 shows that the triple-revolute sparse pattern can be acquired from a
  generated block superset rather than a full dense superset, which is closer
  to the production implementation implied by the paper's Jacobian difficulty.
- v041 shows the cached sparse pattern can be refreshed and repaired without
  dense Jacobians, so the sparse-AD backend has a credible miss-handling policy
  rather than only an offline validation story.
- v042 shows the same backend works when revolute axis constraints depend on
  both parent and child orientations in a skew-axis lower-pair geometry, not
  only in planar/global-axis chains.
- v043 shows the formulation is not limited to revolute joints by adding a
  skew prismatic sliding lower-pair residual with exact dense-pattern agreement.
- v044 shows the prismatic result is not only a single-body slider by adding an
  interbody parent-child prismatic joint, again with exact dense-pattern
  agreement.
- v045 shows the prismatic sparse-AD bottleneck is not solved by simply
  switching from column coloring to row coloring, even though row coloring
  reduces seed count.

Boundary of the claim:

- The paper's TFE method has not been fully reimplemented here. v024 only proves
  that a simple direct Lobatto node swap is not enough.
- The local full-DAE benchmarks now include planar double- and triple-revolute
  chains, but not a broad production-MBD suite with varied lower pairs and
  contact.
- v045 is still a generic AD assembly experiment, and row-VJP remains slower
  than dense `jacfwd` at 138D. Production use needs component/block assembly,
  mixed revolute-prismatic or cylindrical rotating-axis chains, and larger
  benchmarks.

## Compared With Kissel/Negrut/Taves rA Absolute-Coordinate Work

The SBEL/Negrut line is important because it is reproducible and grounded in
absolute-coordinate MBD. Locally, v003 preserves that reference path.

Where the local path improves on it:

- The quaternion residual is more compact than an unconstrained rotation-matrix
  representation while preserving Lie-group updates on `S^3`.
- The local solver directly differentiates nonlinear multiplier-dependent
  friction loads with AD, instead of requiring case-by-case hand sensitivities.
- v013-v035 test higher-order Gauss/adaptive behavior and full revolute
  frictional constraints, while the reproduced rA path is mainly a first-order
  baseline in this workspace.

Boundary:

- rA may still be attractive in large industrial codes because constraints can
  be written directly with rotation matrices and because mature code paths
  matter. The local evidence is numerical-method evidence, not a replacement
  for a full rA production benchmark.

## Compared With Trapezoidal, BDF, Lobatto, Generalized-Alpha, RATTLie

Local conclusions:

- Trapezoidal: v016 gives trapezoidal a favorable reduced-coordinate setup, yet
  Gauss6 is orders of magnitude more accurate and has better conservative
  long-run energy behavior.
- BDF2/BLieDF direction: v017 shows BDF2 is a useful damping/robustness
  baseline, but it is not a high-accuracy winner in these tests.
- Lobatto/TFE-style endpoint nodes: v018 reduced Lobatto6 is accurate but slower
  than Gauss6, and v024 direct full-DAE Lobatto fails without the full TFE
  algebraic treatment.
- Generalized-alpha and RATTLie remain serious constrained-mechanics baselines,
  but they are not yet implemented in this workspace, so no stronger claim is
  made here.

## Short Thesis Statement

The local evidence says the best direction is not just "use a higher-order Lie
integrator." It is:

```text
use the paper's S^3/transport insight,
implement the nonlinear friction Jacobian with AD,
use Gauss6 where the friction law is smooth,
use embedded adaptivity where friction is sharp,
and enforce full-DAE constraint consistency inside Newton instead of relying
on after-step projection,
then scale the successful residual with sparse/block Newton linear algebra.
```

v027 is the current strongest trajectory repair for the full one-body revolute
DAE, v028 is the off-axis stress check, and v029 is the first interbody-joint
generalization. v030 identifies the concrete solver-scaling target, and v031
confirms it in the actual Newton loop. v032 shows the matrix-free version needs
preconditioning, and v033 shows simple Jacobian lagging is not enough. v034
proves colored sparse AD is correct, and v035 makes it fast by batching color
seeds in a compiled JVP. v036 removes dense warm-up pattern discovery with a
conservative block-symbolic mask. v037 recovers the exact observed fine pattern
from that mask without dense Jacobians. v038 shows one cached pattern can be
reused across nearby friction regimes and a longer horizon. v039 shows the
sparse-AD backend transfers to a 207D triple-revolute chain. v040 replaces that
chain's full-superset shortcut with generated block sparsity. v041 adds
generated-block cache refresh/union and repairs an intentionally stale cache.
v042 moves from planar/global-axis joints to skew parent-child revolute axes.
v043 adds the first prismatic lower-pair test and v044 lifts it to an interbody
parent-child chain. Together they separate a correctness improvement from a
speed improvement: exact sparse-pattern recovery is useful, but current
non-revolute patterns still favor dense `jacfwd`. v045 reduces the color count
with row-VJP but shows reverse-mode overhead remains. The next required step is
component/block assembly and testing mixed revolute-prismatic or cylindrical
chains where the prismatic axis rotates with a moving parent.
