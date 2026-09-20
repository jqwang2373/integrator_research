# Version Tree

This file is the human-readable map of the experiment lineage. The detailed
per-version ledger is in `VERSION_LEDGER.md`, the machine-readable ledger is in
`version_ledger.csv`, the numerical-order proof/status ledger is in
`ORDER_PROOF_LEDGER.md`, and the plotted progression is
`version_progression.png`.

## Lineage

```text
external references
  |
  +-- v003 SBEL/Negrut rA reproduction
  |
  +-- v046 ASME four-example validation anchor
  |
  +-- v048 cross-paper same-test benchmark harness
  |
v001 SO(3) benchmark infrastructure
  |
  +-- v002 corrected CF4/RKMK4 right-action kinematics
  |
  +-- v004 Yoshida-composed Lie midpoint for conservative mechanics
        |
        +-- v005 Gauss-Legendre Lie4 smooth rigid-body mechanics
              |
              +-- v006 reduced fixed-pivot DAE with recovered multiplier
                    |
                    +-- v007 absolute-coordinate Gauss DAE stage solve
                          |
                          +-- v008 endpoint-constrained DAE solve
                                |
                                +-- v009 frictional endpoint DAE
                                      |
                                      +-- v010 JAX Jacobian backend
                                      |
                                      +-- v011 S^3 transport operator check
                                            |
                                            +-- v012 quaternion endpoint DAE
                                                  |
                                                  +-- v013 Gauss6 quaternion endpoint DAE
                                                        |
                                                        +-- v014 smoothness decision boundary
                                                        |
                                                        +-- v015 adaptive embedded Gauss64
                                                        |
                                                        +-- v016 Lie-trapezoidal baseline
                                                        |
                                                        +-- v017 Lie-BDF2 baseline
                                                        |
                                                        +-- v018 Lie-Lobatto/TFE-style baseline
                                                        |
                                                        +-- v019 lambda-dependent friction
                                                              |
                                                              +-- v020 adaptive lambda-friction
                                                                    |
                                                                    +-- v021 Brown-McPhee lambda-friction
                                                                          |
                                                                          +-- v022 reduced revolute Brown-McPhee
                                                                                |
                                                                                +-- v023 absolute revolute DAE
                                                                                      |
                                                                                      +-- v024 direct Lobatto full DAE test
                                                                                      |
                                                                                      +-- v025 projected full DAE repair
                                                                                      |
                                                                                      +-- v026 stage pivot-velocity DAE repair
                                                                                            |
                                                                                            +-- v027 stage pivot-velocity+acceleration DAE repair
                                                                                                  |
                                                                                                  +-- v028 off-axis full-axis DAE stress test
                                                                                                        |
                                                                                                        +-- v029 double-revolute interbody DAE
                                                                                                              |
                                                                                                              +-- v030 double-revolute Jacobian sparsity diagnostics
                                                                                                                    |
                                                                                                                    +-- v031 sparse Newton double-revolute loop
                                                                                                                          |
                                                                                                                          +-- v032 matrix-free Newton-Krylov diagnostic
                                                                                                                          |
                                                                                                                          +-- v033 lagged sparse Newton diagnostic
                                                                                                                          |
                                                                                                                          +-- v034 colored-JVP sparse Jacobian diagnostic
                                                                                                                                |
                                                                                                                                +-- v035 batched colored-JVP sparse Jacobian
                                                                                                                                      |
                                                                                                                                      +-- v036 block-symbolic sparse pattern
                                                                                                                                            |
                                                                                                                                            +-- v037 JVP-pruned sparse pattern discovery
                                                                                                                                                  |
                                                                                                                                                  +-- v038 cached sparse pattern reuse
                                                                                                                                                        |
                                                                                                                                                        +-- v039 triple-revolute larger-topology scaling
                                                                                                                                                              |
                                                                                                                                                              +-- v040 generated block triple pattern
                                                                                                                                                                    |
                                                                                                                                                                    +-- v041 triple pattern cache refresh
                                                                                                                                                                          |
                                                                                                                                                                          +-- v042 skew-axis triple-revolute lower-pair
                                                                                                                                                                                |
                                                                                                                                                                                +-- v043 skew prismatic lower-pair
                                                                                                                                                                                      |
                                                                                                                                                                                      +-- v044 double-prismatic interbody lower-pair
                                                                                                                                                                                            |
                                                                                                                                                                                            +-- v045 row-colored VJP sparse AD diagnostic
                                                                                                                                                                                                  |
                                                                                                                                                                                                  +-- v047 cylindrical lower-pair pipeline scaffold
```

## Version Records

Current v047 paper-facing interpretation: v047 is a conditional formal-order
comparison in the current artifact scope. The Gauss6/FullVA path is sixth
order, records smooth position/velocity orders 7.161/7.066, and is compared
only with the local paper-style `m=3` Gauss-Lobatto TFE formula target of
expected order five. It has four-example coverage with dynamic-order evidence
on single/double pendulum and closed-loop residual/reaction evidence on
four-link/slider-crank.
`ORDER_ACCEPTANCE_GATE.md` keeps that distinction machine-checkable: the
closed-loop examples are coverage-only for external dynamic order. The local paper-style `m=3`
Gauss-Lobatto TFE formula target has expected order five. The independent
full-TFE stage replacement remains an optional stronger source-paper
reproduction gate, not the main claim.

| Version | Main Change | What It Proved | Why Keep Moving |
| --- | --- | --- | --- |
| v001 | Built reproducible SO(3) benchmark scripts. | We had stable error/invariant measurements. | No corrected high-order winner yet. |
| v002 | Corrected right-action CF4/RKMK4 formulas. | Fourth-order prescribed attitude kinematics works. | Kinematics is not constrained/frictional dynamics. |
| v003 | Reproduced SBEL/Negrut rA code path locally. | The lab reference baseline is reproducible. | Tested dynamics was roughly first order and rotation-matrix based. |
| v004 | Added Yoshida-composed Lie midpoint. | Fourth-order conservative mechanics with good invariants. | Negative substeps are a poor fit for friction/contact. |
| v005 | Added two-stage Gauss-Legendre Lie4. | Smooth mechanics accuracy/invariants improved without negative substeps. | Still no DAE constraints. |
| v006 | Added reduced fixed-pivot DAE and recovered pivot reaction. | Gauss-Lie4 keeps fourth order with exact reconstructed constraints. | Multipliers were recovered, not solved in a full absolute DAE. |
| v007 | Added absolute-coordinate stage DAE with multipliers. | Position+velocity+acceleration consistency is needed for index-3 behavior. | Endpoint projection was still outside Newton. |
| v008 | Added endpoint variables and endpoint constraints. | Removed post-step endpoint projection while keeping near-fourth order. | Jacobian cost grew and friction was still absent. |
| v009 | Added regularized friction to the endpoint DAE. | Smooth friction keeps high order; sharp friction causes order reduction. | Newton Jacobians were still finite-difference. |
| v010 | Replaced finite-difference Jacobian with JAX AD. | Same solution, roughly 30-40x warm speedup in local tests. | Needed explicit quaternion S^3 transport validation. |
| v011 | Implemented `Pi(g)=g_p T_exp + g_theta` and `Theta(g)`. | Transported quaternion derivatives match direct AD to roundoff. | Operator check needed embedding into the actual residual. |
| v012 | Moved endpoint DAE to unit quaternions on S^3. | Matched SO(3) residual behavior while preserving unit norm. | Only fourth-order Gauss endpoint method. |
| v013 | Added three-stage Gauss6 endpoint collocation. | Smooth friction reached near-sixth order at small extra cost. | Sharp friction still order-reduced. |
| v014 | Swept friction smoothness. | Gauss6 is best when friction is smooth enough; marginal near nonsmooth transitions. | Needed adaptivity for sharp transitions. |
| v015 | Added embedded adaptive Gauss6/Gauss4. | High-accuracy sharp-friction runs beat global fixed-step halving. | Still simplified friction and no multiplier-dependent load. |
| v016 | Added favorable Lie-trapezoidal baseline. | Gauss6 beat trapezoidal on accuracy and long-run energy behavior. | Baseline was reduced, not full TFE. |
| v017 | Added Lie-BDF2 baseline. | BDF2 is useful as damping/robustness baseline but not accuracy winner. | Full constrained BLieDF comparison remains open. |
| v018 | Added Lobatto endpoint-node baseline. | Lobatto6 is accurate but slower than Gauss6 in local tests. | Full TFE formulation may still help conditioning. |
| v019 | Added lambda-dependent Stribeck-style friction. | AD handles coupled friction/multiplier Jacobian directly. | Friction law was still simplified. |
| v020 | Added adaptive lambda-friction. | Sharp lambda-friction benefits strongly from adaptivity. | Needed Brown-McPhee-style friction. |
| v021 | Added Brown-McPhee-style lambda friction. | Smooth case favors fixed Gauss6; sharp case benefits from adaptive Gauss64. | Still fixed-pivot surrogate. |
| v022 | Added reduced revolute Brown-McPhee pendulum. | Paper-like scalar revolute case confirms fixed Gauss6 for smooth friction and adaptive Gauss64 for sharp friction. | Still not a full absolute-coordinate index-3 DAE. |
| v023 | Added absolute-coordinate quaternion revolute DAE with five constraints. | Gauss6 is much more robust than Gauss4; sharp Gauss4 fails where Gauss6 succeeds. | Endpoint velocity/acceleration constraint treatment is still missing. |
| v024 | Added direct Lobatto endpoint-node collocation to the full revolute DAE. | A simple Gauss-to-Lobatto node swap fails with rank-deficient/divergent Newton residuals. | Need true TFE weighted-residual or other index-3 algebraic stabilization. |
| v025 | Added SHAKE/RATTLE-style endpoint projection to the full revolute DAE. | Projection removes endpoint drift and rescues sharp Gauss4 convergence, but costs trajectory accuracy. | Need constraint treatment inside the residual, not only after-step projection. |
| v026 | Added stage pivot-velocity constraints inside the full revolute residual. | Endpoint velocity drift drops by about four orders for Gauss6, and sharp Gauss4 convergence is rescued without projection. | Need full lower-pair velocity/acceleration consistency, not just pivot velocity. |
| v027 | Added stage pivot-acceleration constraints inside the full revolute residual. | Endpoint velocity drift drops to about 1e-12 for Gauss6 PivotVA, and stage pivot acceleration is enforced to machine precision. | Need to generalize from pivot acceleration in one revolute joint to all lower-pair acceleration constraints and TFE weighted residuals. |
| v028 | Added off-axis torque and explicit hinge-axis velocity/acceleration residuals. | FullVA drives axis acceleration diagnostics to about 1e-25, but does not change trajectory relative to PivotVA. | Single revolute axis is not the remaining bottleneck; move to multi-joint/general lower-pair treatment. |
| v029 | Added a two-body double-revolute DAE with interbody Brown-McPhee friction. | PivotVA/FullVA converges on an interbody joint and reduces Gauss6 endpoint velocity drift by about seven to eight orders. | Need sparse/block Newton solves and less planar lower-pair tests. |
| v030 | Diagnosed v029 Newton Jacobian sparsity and dense-vs-CSR solve cost. | Gauss6 double-revolute Jacobians are only about 3% dense, and CSR solves are orders faster than dense solves for the 138D systems. | Need integrate sparse/block solves into Newton and avoid dense AD materialization. |
| v031 | Integrated CSR sparse linear solves into the double-revolute Newton loop. | Gauss6 FullVA keeps dense-equivalent trajectories while cutting end-to-end runtime by 22x-31x on the targeted h=0.02 tests. | Need avoid dense JAX Jacobian materialization and test larger/general lower-pair topologies. |
| v032 | Tested matrix-free JAX JVP plus unpreconditioned GMRES for Gauss6 FullVA. | JVP is correct to roundoff, but unpreconditioned GMRES fails after 200 iterations while CSR direct solve succeeds quickly. | Need preconditioned Krylov or structured sparse/block Jacobian assembly, not plain GMRES. |
| v033 | Tested lagged/modified sparse Newton with reused CSR Jacobians. | Lagging preserves trajectory to roundoff scale, but extra Newton work offsets fewer Jacobian evaluations; best speedup is only 1.06x. | Need structured sparse/block assembly or preconditioners rather than simple Jacobian lagging. |
| v034 | Tested column-colored JAX JVP sparse Jacobian assembly. | Colored JVP matches dense Jacobian values to 1e-18--1e-16 relative error, but is slower than dense `jacfwd` on the 138D system. | Need hand/block sparse assembly, compiled/batched coloring, or larger topology before sparse AD wins. |
| v035 | Batched all colored JVP seed directions in one compiled `vmap(jvp)` call. | Batched colored JVP matches dense Jacobian to 4.53e-18 relative error and beats dense `jacfwd` CSR by 2.49x--2.66x on the 138D double-revolute tests. | Need symbolic/block sparsity patterns and larger lower-pair chains; current mask still comes from dense warm-up. |
| v036 | Replaced dense warm-up pattern discovery with a conservative block-symbolic sparsity pattern. | The block pattern misses zero dense entries and builds in milliseconds; sharp block-symbolic runtime is 0.050s vs dense `jacfwd` 0.079s. | The mask is conservative: 1755 entries and 34 colors vs warm-up 582 and 11; needs finer generated symbolic pattern and larger chains. |
| v037 | Pruned v036's block-symbolic superset with batched JVP dry-runs instead of dense Jacobians. | The pruned pattern exactly matches dense warm-up at 582 entries and 11 colors with zero missing entries; build time is 0.053-0.067s vs dense warm-up 0.952-1.082s. | Still path-sampled rather than a formal symbolic proof; needs larger-chain validation and pattern-cache policy. |
| v038 | Cached one smooth-case JVP-pruned pattern and reused it for longer smooth/sharp solves. | The cached pattern misses zero entries against T=0.12 dense validation in both cases and gives 1.49x runtime speedup vs dense `jacfwd` CSR. | Only tested on planar double-revolute and T=0.12; needs larger topology and broader state coverage. |
| v039 | Extended the sparse-AD FullVA benchmark to a three-body triple-revolute chain. | The 207D Newton system has a 930-entry, 11-color JVP-pruned pattern with zero dense-validation misses; runtime improves by 1.41x smooth and 1.67x sharp versus dense `jacfwd` CSR. | Pattern discovery still uses a full superset in this first larger-topology version; needs generated block superset/cache and longer/larger chain validation. |
| v040 | Replaced v039's full-matrix superset with a generated triple-revolute block superset. | The generated 2691-entry/32-color superset has zero dense-validation misses, and JVP pruning recovers the exact 930-entry/11-color dense pattern with 2.14x smooth and 1.78x sharp speedups versus dense `jacfwd` CSR. | Still path-sampled on a short planar triple-revolute horizon; needs cache refresh/union rules and larger less-planar lower-pair validation. |
| v041 | Added a generated-block cache refresh/union policy for triple-revolute patterns. | A smooth short cache transfers to four longer nominal/perturbed smooth/sharp scenarios with zero dense-validation misses; a stale-cache audit removes 23 entries and refresh restores all of them. | Still planar triple-revolute only; needs less-planar lower-pair systems and larger-chain validation. |
| v042 | Replaced global-axis triple-revolute constraints with skew parent-child axis alignment. | The 207D non-coplanar residual has a 2181-entry/31-color pruned pattern exactly matching dense validation; endpoint velocity is around 1e-16 and sparse runtime is 1.94x-1.98x faster than dense `jacfwd` CSR. | Still short-horizon three-body revolute only; needs larger skew-axis chains and other lower pairs. |
| v043 | Added a skew-axis prismatic lower-pair residual with sliding friction. | The 69D prismatic residual has a 414-entry/18-color pruned pattern exactly matching dense validation, and dense/sparse trajectories match exactly with endpoint velocity constraints around 1e-17. | Sparse AD is slower than dense `jacfwd` on this small system; needs interbody prismatic/cylindrical chains. |
| v044 | Added a two-body double-prismatic chain with an interbody prismatic joint. | The 138D residual has a 2439-entry/90-color pruned pattern exactly matching dense validation, and dense/sparse trajectories match to roundoff with endpoint velocity constraints around 1e-16. | Sparse AD is still slower than dense `jacfwd` because 90 colors are too many; needs finer coloring/block structure and rotating-axis prismatic/cylindrical tests. |
| v045 | Reassembled the v044 exact sparse pattern with row-colored batched VJP. | Row coloring reduces seeds from 90 column colors to 54 row colors, with roundoff trajectory agreement; smooth row-VJP is 1.04x faster than column-JVP. | Row-VJP remains slower than dense `jacfwd`, so reverse-mode overhead or component/block assembly is still the bottleneck. |
| v046 | Validated the upstream ASME rA path on all four repository examples. | The four-example harness now records convergence, constraints, SO(3) diagnostics, runtime, and plots for single pendulum, double pendulum, four link, and slider crank. | Future local Gauss6/FullVA variants must pass this four-example gate, not only toy mechanism checks. |
| v047 | Started the cylindrical lower-pair pipeline scaffold. | The 132D cylindrical residual has a 2637-entry/90-color JVP-pruned pattern exactly matching dense validation, row-VJP assembly of the same pattern reduces seeds to 60 row colors while preserving roundoff trajectory agreement, and a five-repeat warmed benchmark records median row/column runtimes 1.008x smooth and 0.990x sharp while dense `jacfwd` remains faster with dense/row 0.873x and 0.819x; a sparse-speed gap audit records row-VJP speedups needed 1.145x smooth and 1.220x sharp to match dense, and a sparse cost-model audit records runtime reductions needed 12.7% smooth and 18.1% sharp to match dense, or 21.4% smooth and 26.3% sharp for a 10% dense win; endpoint velocity constraints are around 2e-16 after projection, endpoint-projection audit orders 5.817/5.796 smooth and 4.089/4.202 sharp for raw residual/correction, an endpoint KKT residual closure with smooth/sharp position-velocity orders 7.161/7.066 and 1.894/2.683 plus endpoint velocity residuals below 3.8e-16, an endpoint TFE gap audit with finest KKT/projection correction ratios 0.213 smooth and 0.999 sharp while stage equations remain non-TFE-weighted, an endpoint TFE candidate audit with endpoint-node weighted rows and max candidate residuals 1.177e-12 smooth and 5.723e-13 sharp, a solved endpoint-node candidate audit with max solved residuals 6.643e-14 smooth and 5.723e-12 sharp, a stage-weighted candidate audit with max weighted residuals 6.819e-15 smooth and 3.017e-13 sharp, a stage-functional specification audit with six independent weak/TFE row families totaling the 132-row stage budget, a stage-functional implementation audit over the smooth/sharp h-sweep with max equivalence norm 1.755e-17 while remaining Gauss6-equivalent, a non-equivalent stage probe audit with max probe norm 8.352e-11 evaluated but not solved as residual rows, a stage-probe boundary-source audit with 36 block/h rows, max lift error 0.000e+00, and max lift-ratio deviation 2.220e-16, a stage-probe source-budget audit with 6 case/h rows, max aggregate lift-ratio deviation 3.331e-16, and dominant `newton_euler_weak_balance` source families, a stage-probe dominant-source split audit with 24 component/h rows, max component lift-ratio deviation 2.220e-16, and body0 translational balance as the dominant next weak-row target, a stage-probe block-order audit with 12 block/case rows, max gap 7.744e-11, and gap-order range 3.918/7.384, a solved non-equivalent stage-probe audit with max residual 2.192e-12 and max probe norm 8.383e-11, a stage-probe beta homotopy with 30 one-step rows, max residual 4.029e-15, and max probe norm 2.348e-11, a stage-probe block-activation audit with 36 isolated block rows, max residual 1.696e-15, and max activated probe norm 2.177e-11, a stage-probe component-activation audit targeting body0 translational balance with 6 isolated component rows, max residual 1.195e-15, max activated component probe norm 2.006e-11, and max lift-ratio deviation 2.220e-16, a stage-probe component-formula audit with 6 direct formula rows, max residual 1.258e-15, zero formula/generic component difference, and max lift-ratio deviation 2.220e-16, a stage-probe Newton-Euler formula audit with 6 direct block-formula rows, max residual 1.265e-15, zero formula/generic block difference, and max lift-ratio deviation 3.331e-16, a stage-probe all-source formula audit with 6 direct 132-row formula rows, max residual 4.029e-15, zero formula/generic stage-major and block differences, and max lift-ratio deviation 3.331e-16, a stage-probe all-source trajectory bridge audit with 6 complete trajectory rows, max residual 2.192e-12, max formula probe 8.383e-11, and max position/velocity reference errors 9.45e-06/2.36e-03, a full-stage acceptance gap audit preserving the full-TFE blockers, a stage-local source-removal target audit mapping 36 endpoint-boundary source rows to six stage-local weak-row targets, a stage-probe coupled-budget audit with max beta1/isolated-L2 deviation 1.480e-02 and max solved/beta1 probe ratio 1.292e+02, a stage-probe trajectory-accumulation audit with max solved/beta1 ratio 1.292e+02 and max per-step ratio 1.615e+01, a stage-probe beta-trajectory bridge audit with 18 trajectory rows over beta=[0,0.5,1], max residual 2.192e-12, and max probe norm 8.383e-11, a stage-replacement design audit with the 132-row stage budget, solved 40-row endpoint extension, and source-budget evidence recorded while the independent full-TFE stage functional remains missing, paper formula mapping and derivative-operator audits for the m=3 Lobatto x-to-y/z map, a paper stage-input-map audit covering all 132 v047 stage rows across six row families, a paper multiplier-policy audit specifying lambda_x/lambda_yz dimensions 24/48 with no extra lambda_y/z residual rows, a paper kinematic-formula audit deriving four kinematic row-family formulas across 72 stage rows with max residual 7.26e-18 while not substituting them into Newton, a paper balance/constraint-formula audit deriving the remaining Newton-Euler weak-balance and lower-pair constraint row-family formulas across 60 stage rows with max residual 4.34e-19 while not substituting them into Newton, a paper position-substitution candidate replacing two paper position row families inside Newton (36 stage rows, max residual 5.68e-12, rank 132, smooth/sharp orders 1.227/0.731 and 1.165/2.464) but remaining order-limited, a paper kinematic-substitution candidate replacing four paper kinematic row families inside Newton (72 stage rows, max residual 9.57e-12, rank 132, max condition 8.81e11, smooth/sharp orders 1.406/1.542 and 1.400/1.237) but remaining diagnostic-z0/order-limited, a paper all-row substitution candidate combining all six paper row families in one 132-row Newton residual (max residual 9.64e-12, full rank 132, max condition 1.62e13, smooth/sharp orders 1.406/1.542 and 1.400/1.237) but remaining diagnostic-z0/order-limited, a paper all-row Gauss-z0 diagnostic repeating the six-family/132-row substitution with a baseline-Gauss extrapolated start acceleration (max residual 7.70e-12, full rank 132, max condition 1.58e13, max z0 delta 1.69e1, smooth/sharp orders 1.410/1.573 and 1.395/1.170), showing the low-order blocker is not removed by replacing axis-z0 alone, a paper all-row Gauss-z0 terminal-output diagnostic solving the same six-family/132-row residual from the terminal paper Lobatto node (max residual 9.20e-12, full rank 132, max condition 1.58e13, terminal-vs-Gauss position/velocity deltas 3.19e-03/1.82e-02, smooth/sharp orders 2.494/1.780 and 1.029/0.107), a paper all-row recurrent-z0 terminal-output diagnostic keeping the all-row residual and terminal paper output while recurring terminal paper z after one Gauss bootstrap (max residual 9.09e-12, full rank 132, max condition 1.58e13, max used-z0-vs-Gauss delta 4.16e-01, smooth/sharp orders 4.557/4.667 and 2.579/1.925), a paper all-row consistent-z0 terminal-output diagnostic removing that bootstrap with an instantaneous 20D solve (max residual 9.79e-12, full rank 132, max condition 1.58e13, smooth/sharp orders 4.046/4.420 and 2.554/1.918), a paper all-row consistent-z0 conditioning audit localizing the near-null lower_pair_index3_weak_constraints/lower_pair_lambda blocker (6 rows, max raw/equilibrated condition 1.58e13/5.07e4), a paper family-ablation diagnostic solving 12 one-step rows over two five-family variants with max residual 7.286e-12, full rank 132, max raw/scaled conditions 1.58e13/1.39e5, and lower-pair/lambda near-null localization in all rows, a paper lower-pair direct-source residual-substitution audit verifying raw lower-pair plus lifted C_v balance to 1.821e-13 over 6 trajectory rows while full=false, a paper lower-pair residual-derived stage-source audit reconstructing C_hat_i from raw residual rows with max derived-vs-direct gap 1.289e-12, max stage-consistency gap 1.406e-14, and zero derived balance error while full=false, a paper lower-pair self-consistent endpoint-source audit computing C_v(x_terminal) inside Newton with max residual/balance/source 9.441e-12/1.821e-13/7.974e-06 and no external trajectory source while full=false, a paper lower-pair source-free elimination rank audit recording 6 trajectory rows, max stage-consistency gap 1.406e-14, rank 16 for 24 lower-pair stage rows, and an 8-row missing mean-source closure budget, a source-free mean-velocity closure audit solving 6 smooth/sharp h-sweep rows with max residual 8.13e-12 and no endpoint source, terminal-row replacement, or projection, a source-free final-stage velocity closure audit solving 6 smooth/sharp h-sweep rows with max residual/raw terminal velocity 9.49e-12/4.01e-16 and no endpoint source, terminal-row replacement, or projection while smooth position order remains 3.523, a source-free mean-blend closure audit sweeping 7 alpha values over 42 one-step rows with best alpha 0 and max residual/raw terminal velocity 5.489e-12/2.337e-10 while still not accepted, a source-free mean-blend trajectory audit promoting alpha 0 to 6 trajectory rows with max residual/raw terminal velocity 9.453e-12/8.234e-06 and smooth/sharp orders 5.317/6.782 and 2.555/1.918 while terminal closure remains open, a source-free mean-blend trajectory alpha sweep testing 7 alpha values over 42 trajectory rows with best alpha 0.75, max residual/raw terminal velocity 8.779e-12/7.447e-06, and minimum orders 2.555/1.918 while still terminal-open, a source-free terminal-velocity extrapolation trajectory audit plus a source-free terminal-extrapolation blend trajectory audit with max residual/raw terminal velocity 9.910e-12/1.182e-05, smooth/sharp orders 3.518/4.748 and 2.554/1.917, and worst/smooth component-blend terminal ratios 1.585/0.147 while still not full TFE, a centered terminal-velocity bridge audit with 18 trajectory rows over gamma=[0,0.5,1], best terminal velocity 4.01e-16, and smooth-order/full=false caveats, a lower-pair closure acceptance matrix audit comparing 14 candidate closures with 0 accepted candidates, a source-free final-stage velocity closure audit with terminal velocity closed but smooth-order/full=false caveats, and a paper residual-substitution contract audit mapping six row-family targets with 6 formulas, 6 substituted rows, 0 accepted h-sweep rows, and full=false, an endpoint TFE readiness audit with 31 satisfied/38 partial/1 missing check, high smooth-case observed order after initial velocity compatibility repair, a Brown-McPhee smoothness sweep with position/velocity orders 7.161/7.066, 6.494/5.657, 3.392/4.511, and 1.894/2.683 at stribeck velocities 0.50/0.20/0.10/0.05, a sharp adaptive step-doubling diagnostic that reduces vs=0.05 velocity error from 5.70e-05 at fixed h=0.01 to 3.81e-07 at 3.2x runtime plus an adaptive tolerance/work fit with velocity slopes 0.881 all-points and 1.710 prefix plus a reference-floor flag, a sharp fixed-refinement audit with all-point position/velocity orders 3.294/5.867 plus tail orders 5.364/8.437, a deep sharp fixed-refinement audit with all-point position/velocity orders 6.398/5.870 plus tail orders 7.423/3.177, and an ultra sharp fixed-refinement audit with all-point position/velocity orders 7.521/5.725 plus tail orders 7.626/8.279, a sharp refinement cost-envelope audit with the h=0.00125 high-order window costing 7.76x runtime and reducing velocity error by 1.06e6x versus h=0.01, a v046 ASME gate table, exact single-pendulum driven kinematics plus a full absolute-coordinate driven FullVA residual, embedded scalar FullVA bridge, reaction-multiplier reconstruction, accepted double-pendulum FullVA reference policy, a v046 double diagnostic whose error halves when the v046 reference step is halved, a four-example lower-pair constraint-graph bridge covering four_link and slider_crank DP1/CD/DP2/D rows, a four-example `Phi_q` full-row-rank audit, accepted local closed-loop kinematic FullVA solves for four_link/slider_crank, accepted reaction-dynamics rows for those driven examples, a nonlinear-capacity audit with 216 rows across six finite-difference source-feature families, 0 spans, best projection residual 6.952e-01, and best correction residual 7.012e-01, a higher-order/nonlocal capacity audit with 216 rows over third-differential and same-case cross-step source features, 0 spans, best projection residual 6.952e-01, and best correction residual 7.012e-01, a weak-row structure-capacity audit with 216 rows over source/active cross-Gram, Hadamard, cross-Hadamard, and shifted-commutator source-active feature families, 0 spans, best projection residual 6.952e-01, and best correction residual 7.012e-01, an h-adaptive endpoint-pose velocity response audit with terminal_closed_row_count=1, smooth_order_ok_count=0, accepted_candidate_count=0, and order_terminal_intersection_present=false, a lower-pair candidate frontier audit aggregating 11 families and 115 rows with 35 terminal-closed candidates, 17 smooth-order candidates, order_terminal_intersection_count=0, a bounded tangent requirement audit with requirement_row_count=7, row_space_oracle_span_count=36, target_free_formula_span_count=0, and bounded_gradient_practical_cap_spanning_row_count=12 preserving the stage-local weak-row tangent as the next repair target, a recurrent stage2 feature-dictionary span audit with feature_dictionary_row_count=12, span_row_count=8, combined_all_dictionary_span_count=2, best dictionary stage2_matrix_core at residual 1.084e-14, and formula_coefficient_law_present=false, a recurrent stage2 frozen coefficient-law screen with coefficient_law_row_count=60, span_count=0, best law closure_delta_norm_weights at residual 5.596e-01, coefficient_derivative_included=false, target_jacobian_used_for_formula=false, and full=false, a recurrent stage2 state-feature coefficient-derivative screen with state_feature_coefficient_derivative_row_count=36, span_count=0, best law inverse_closure_delta_norm_weights_derivative at residual 5.908e-01, coefficient_derivative_included=true, target_jacobian_used_for_formula=false, and full=false, a four-history recurrent source-law screen with terminal_closed_row_count=0, smooth_order_ok_count=2, best terminal velocity 2.950e-07, best smooth min order 5.342, and full=false, and a read-only output validator over 292 generated result files, 147 CSV tables, 120 PNG plots, summary gate status, stale wording, and README/report artifact lists. | Row-VJP has a quantified cost-model target but is not yet a dense-`jacfwd` speed win; full TFE stage replacement remains pending, and coarse sharp-friction order remains reduced but ultra refinement recovers high order. |

| v048 | Added the cross-paper same-test benchmark harness. | The harness writes a 17-row external run plan, estimates and executes the full 2021 public order-policy workload at 326700 public-code steps, completes all 9/9 `rA/rp/reps` public step-size trio groups for `single_pendulum`, `four_link`, and `slider_crank` as 27/27 ok rows, adds 9/9 public `double_pendulum` dynamic self-reference order rows for `rA/rp/reps`, completes 12/12 public timing/iteration policy rows for `rA/rp/reps` on all four examples at `T=3`, `h=1e-3`, completes a bounded same-mechanism `Gauss6/FullVA` single-pendulum pilot with observed orders `6.073/6.033/6.055/6.024`, adds a 3/3 exact public-horizon `Gauss6/FullVA` single-pendulum step-size trio at `T=3`, `h=[1e-2,1e-3,1e-4]` (roundoff-limited final-error orders), adds 6/6 selected closed-loop `Gauss6/FullVA` residual rows on the 2021 `four_link` and `slider_crank` mechanisms with max dynamics residuals `1.338e-13/6.492e-15`, adds 6/6 public-horizon closed-loop residual rows for those mechanisms at `T=3`, `h=[1e-2,1e-3,1e-4]` with finest-row max dynamics residuals `5.136e-13/1.113e-14`, adds a coarse-first public-horizon `double_pendulum` `Gauss6/FullVA` tranche at `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`, with position/velocity orders `7.951/7.042`, adds matching coarse same-window public `double_pendulum` baselines where `rA/reps` complete 6/6 rows with position/velocity orders `0.703/0.754` while `rp` records three Newton nonconvergence rows, adds a single-pendulum coarse same-window tranche with 9/9 public rows, 3/3 local `Gauss6/FullVA` rows, and a 4-row work/precision summary at `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`, with local position order `6.054`, adds 12/12 selected same-window public-`rA` dynamics versus local-`Gauss6/FullVA` comparison rows at `T=0.2`, `h=[0.02,0.01,0.005]`, adds 9-row public order/work, 4-row same-window work/precision, 3-row double coarse work/precision, 4-row single coarse work/precision, a 2-row closed-loop surrogate dynamic gate with `accepted_dynamic_order_count=0`, a 2-row closed-loop dynamic error floor audit with two position/reference-floor blockers and `accepted_dynamic_order_count=0`, a closed-loop coarse dynamic-order probe with `11/12` ok rows and `accepted_dynamic_order_count=0`, and 4-row coarse-first readiness gate CSVs with `coarse_first_ready_examples=2/4`, `closed_loop_surrogate_available=2`, `closed_loop_floor_audit_available=2`, and `coarse_first_dynamic_order_missing=0`, writes a 48-row four-example performance matrix with 32 completed and 0 partial rows, adds a bounded 2022 half-implicit four-example pilot with 24/24 ok rows and 8/8 `rA/rA_half` model-form trios, and records an 11-row velocity-partitioning code-path audit covering the EasyChair PDF reference check, public web search, and both local SBEL mirror refs `origin/master` plus `origin/user/aaron/msd`, with 0 exact VP path hits while preserving `same_test_campaign_status=not_run` and `external_superiority_claim=false`. | It is an execution scaffold, not a method result; the public-horizon single-pendulum and closed-loop residual trios are complete but roundoff/reference-floor or residual-only limited, the single/double coarse tranches and matching public coarse baselines are not the public `1e-4` policy, the closed-loop Newton coarse-order artifact now supplies accepted local dynamic-order rows for `four_link`/`slider_crank` within the coarse read-only scope, the coarse-first gate shows `single_pendulum` and `double_pendulum` are currently same-window order/time ready, the closed-loop surrogate, floor audit, and same-window rows are still selected-window residual/table-shape evidence rather than the exact public dynamic order/work campaign, and the full 2022/original-TFE/velocity-partitioning same-test campaigns plus remaining `Gauss6/FullVA` external rows still have to be run before CMAME submission readiness. |

v047 also records a bounded-gradient velocity-compression cap sweep: 288
cap/candidate/case/h rows keep value balance and meaningful non-final energy,
but only 92 span at the tested caps, practical cap 1e12 spans 12 rows, and all
36 local spans require cap 1e18. This keeps the full TFE target at a bounded
analytic derivative-aware coefficient-gradient formula plus a nonlinear
h-sweep.

v047 then adds a bounded-formula saturation-law audit: 648
law/cap/candidate/case/h rows over global tanh, rowwise tanh, and rowwise
rational-quadratic laws keep value balance and meaningful non-final energy,
366 span at the tested caps, and all local spans require cap 1e22 for every
tested law. The correction direction remains a target-direction oracle, so this
is still diagnostic rather than an independent full TFE stage replacement.

v047 also records a paper all-row consistent-z0 terminal-output diagnostic: an
instantaneous 20D acceleration/multiplier solve removes the Gauss bootstrap
(`bootstrap_step_count=0`). A follow-up paper all-row consistent-z0 conditioning
audit records 6 one-step rows, full rank 132, max raw/equilibrated conditions
1.58e13/5.07e4, and the dominant near-null
`lower_pair_index3_weak_constraints`/`lower_pair_lambda` families. Accepted
h-sweep order and full TFE stage replacement remain open. A scaled-Newton
follow-up applies iterative row/column equilibration inside the same all-row
consistent-z0 residual, lowering the max condition diagnostic to 5.13e4 with
3.80e8 raw-to-scaled reduction but leaving the same order limits, so it remains
diagnostic rather than an accepted replacement. A paper family-ablation
diagnostic then solves 12 one-step rows over two five-family variants, keeps
full rank 132 with max residual 7.286e-12, and localizes the near-null family
to `lower_pair_index3_weak_constraints`/`lower_pair_lambda` without accepting
full TFE replacement. A paper lower-pair/lambda Schur diagnostic then solves
6 one-step rows on the same six-family residual, finds a zero direct
lower-row/lambda block and a full-rank reduced Schur block with max condition
5.98e3, and checks the Schur-ordered Newton direction against the raw solve
with max linear residual 1.15e-14 and max relative direction difference
7.79e-09. The later source-free mean-velocity closure candidate fills the rank
audit's missing 8 rows with paper-stage mean-velocity closure rows. It solves
6 smooth/sharp h-sweep rows with max residual 8.13e-12 and no endpoint source,
terminal-row replacement, or projection, but smooth/sharp orders 3.512/4.448
and 2.555/1.918 keep full TFE stage replacement open.
The source-free mean-blend closure audit sweeps 7 alpha values over 42 one-step
rows, keeps endpoint source, terminal-row replacement, and projection removed,
and finds best alpha 0 with max residual/raw terminal velocity
5.489e-12/2.337e-10; it remains local evidence, not accepted full TFE.
The source-free component-blend trajectory audit tests an 8-component alpha
vector from a one-step h=0.02 screen and records max residual/raw terminal
velocity 9.971e-12/7.458e-06, minimum orders 2.555/1.918, and a 1.001
terminal-velocity ratio versus the scalar alpha baseline, so per-component
alpha tuning does not close the terminal-velocity blocker.
The source-free terminal-velocity extrapolation trajectory audit plus a source-free terminal-extrapolation blend trajectory audit replaces the
8 mean-closure rows with terminal-node Lagrange extrapolated Gauss-stage
velocity-constraint rows. It records 6 rows, max residual/raw terminal velocity
9.91e-12/1.18e-05, smooth/sharp orders 3.518/4.748 and 2.554/1.917, and
worst/smooth terminal-velocity ratios versus component-blend 1.585/0.147. It
is a real source-free basis-change diagnostic, but the worst-case sharp coarse
terminal velocity remains worse than component-blend.
A centered terminal-velocity bridge audit tests 16 centered acceleration
source-consistency rows plus 8 terminal-velocity bridge rows over
gamma=[0,0.5,1], closes terminal velocity to 4.01e-16 at gamma 0, and keeps max
residual 9.75e-12, but it uses a terminal-boundary row and loses smooth order,
so it remains diagnostic. A lower-pair closure acceptance matrix compares 14
closure families and accepts 0 candidates:
`source_free_mean_blend_trajectory_best_alpha` is the best
source-free/order-preserving row set, while
`centered_terminal_velocity_bridge` and
`source_free_final_stage_velocity_closure` are terminal-velocity row sets, so
the accepted-order and terminal-closure properties remain split. It keeps
`full_tfe_stage_replacement=false`. A closure property Pareto audit then
groups the same 14 candidates into 5 property-intersection rows and confirms
the empty accepted intersection: 9 candidates are source-free/no-replacement,
5 are order-preserving source-free, and 3 are terminal-velocity closed. The
follow-up closure row-span audit tests the 40-row source-free basis against 8
terminal-bridge target rows over 6 case/h local tangents, finds rank increase
40->48, max projection relative residual 2.814e-01, and an 8-rank
missing-direction complement that reconstructs the target to 9.25e-14 while
remaining terminal-boundary-derived; its column energy is velocity-level, with
angular velocity dominant in all 6 rows, max angular/translation velocity
fractions 0.506/0.496, zero lower-pair-lambda fraction, and translation
acceleration below 5.60e-05. The follow-up velocity-basis span audit tests 7
weighted eight-row stage-velocity closure families plus the 24-row all-stage
velocity upper bound against those same 8 terminal-bridge rows. The all-stage
velocity rows span at max relative residual 2.78e-15, but the best weighted
candidate, `endpoint_lagrange_velocity_closure`, remains at 4.20e-01 and no
weighted candidate spans, so the next repair is an eight-row source-free
compression of the all-stage lower-pair velocity row space. The
velocity-compression audit then fits that eight-row source-free compression
locally: all three fixed candidates span all 6 case/h samples, the best fixed
candidate is `optimized_global_stage_scalar` with weights numerically
`[0,0,1]`, and the best fixed residual is 1.04e-15. The strengthened
selector-degeneracy check shows the fixed fits collapse to that final-stage
selector, with universal full 8x24 selector distance 1.53e-15 and max
non-final-stage energy fraction 1.71e-15. The non-degenerate follow-up sweeps
192 fixed stage-0/stage-1 injection rows; 84 rows have meaningful
non-final-stage energy, but none spans locally and the best meaningful
projection residual is 1.59e-03. The state-local diagonal direction oracle
then sweeps 72 rows over 65 direction samples; 36 rows have meaningful
non-final-stage energy, but none spans locally and the best meaningful
projection residual is 9.90e-03. The non-final full component-mixing follow-up
tests 36 stage-0/stage-1/stage-0+1 full-mixing rows; 0 span locally and the
best tangent residual is 9.81e-01. The value-level source-free probe tests 72
case/h/candidate rows; all 72 balance row values, 18 are value-balanced local
tangent spans, but 0 meaningful non-final value-balanced rows span, with
successful spans final-stage-selector-like at max non-final energy 2.12e-15.
The derivative-aware local oracle then tests 36 non-final rows; all 36 balance
values and span locally with meaningful non-final energy after a
coefficient-gradient correction. The bounded-gradient and bounded-formula
follow-ups keep value balance and meaningful non-final energy but still need
large caps: all derivative-aware local spans require cap 1e18 for the hard-cap
sweep and cap 1e22 for the explicit saturation laws, whose direction remains a
target oracle. The target-direction-free follow-up then tests 2592 rows over
12 source-derived, stage-extrapolated, and all-active component direction laws; all rows remain value-balanced and
meaningful, but 0 span locally and the best residual is 9.82e-01.
The direction-capacity follow-up then tests 216 candidate/feature/case/h rows:
all-stage velocity features span 72 rows at roundoff, but every non-final
active/source feature family has 0 spans; the best non-final residual is
9.81e-01 and the best non-final correction residual is 9.998e-01. The
nonlinear second-differential capacity follow-up then tests 216 rows across six
finite-difference source-feature families; all six families have 0 spans, with
best projection/correction residuals 6.95e-01/7.01e-01. The
higher-order/nonlocal capacity follow-up then tests 216 rows over
third-differential source features and same-case cross-step source deltas; all
six families again have 0 spans, with the same best residuals. The one-step
history-transport capacity follow-up then tests 216 rows over transported
source-row and non-final velocity-row deltas; all six families again have
0 spans, with best projection/correction residuals 7.13e-01/7.12e-01. The
two-step history-transport capacity follow-up then tests 216 rows over two
future transported source/velocity deltas; all six families again have 0 spans,
with best projection/correction residuals 6.95e-01/7.01e-01. The recurrent
history-capacity follow-up then tests 216 rows over two-step curvature and
bilinear source/velocity history features; all six families again have
0 spans, with best projection/correction residuals 6.95e-01/7.01e-01. The
weak-row structure-capacity follow-up then tests 216 rows over source/active
cross-Gram, Hadamard, cross-Hadamard, and shifted-commutator source-active
feature families; all six families again have 0 spans, with best
projection/correction residuals 6.95e-01/7.01e-01. The row-space compression
follow-up then tests 36 rows over target-free SVD, row-norm, and
stage-balanced frozen velocity-space compressions; all six laws again have
0 spans, with best projection residual 7.38e-01 and best non-final residual
9.82e-01. The row-space coefficient-derivative oracle then spans all 36 local
tangents and 24 value-balanced rows with best residual 8.92e-16, but only by
using the target direction and coefficient-gradient norms up to 6.78e18. The
repair is therefore a bounded target-free coefficient-gradient formula, likely
as a revised analytical weak-row formula or richer nonlinear recurrent history
source law plus nonlinear h-sweep. A later
target-free active-stage-velocity matrix grid improves the best local residual
to 0.576548 with `stage2_velocity_shifted_column_broadcast_feature`, but still
has independent target rank 8 and no terminal-bridge span, so it remains
localization evidence rather than an accepted formula. A two-row best-law
missing-direction decomposition keeps that residual and rank-eight gap but
localizes 96.3% of the missing tangent energy to stage 2 with dominant
variable family `angular_velocity_w` at fraction 0.502991. A stage-2
angular-only mask grid then tests 8 rows; its best residual is only 0.752997
with rank 8/no span and a `translation_velocity_v` dominated remaining
direction, ruling out simple angular masking. A direct translation/angular
cross-coupling grid tests 8 outer-cross rows; its best residual is only
0.898812 with `stage2_velocity_angular_to_translation_cross_feature`, rank
8/no span, and a `translation_velocity_v` dominated stage-2-local remaining
direction, excluding simple translation/angular outer-cross rows. An
endpoint-pose generalized-velocity predictor grid then improves the best local
residual to 0.117782 with `paper_endpoint_pose_positive_lagrange_z`, but it
still has rank 8/no span and a mostly stage-0 remaining tangent. A
near-terminal convex screen finds a roundoff span only for the terminal-bridge
equivalent stage-2 law, while the best nonterminal law
`paper_endpoint_pose_stage02_convex_0p05_z` reaches 0.049317 with rank 8/no
span; focused h-scaling reruns keep that nonterminal residual at 0.051890 and
0.052472 for h=0.02 and h=0.01. A synchronized pose/velocity near-terminal
row improves to 0.009512 with `stage02_convex_pose_velocity_0p01_z`, but
h=0.02/h=0.01 stay near 0.01 and rank 8/no span. Terminal-limit extrapolation
reaches 4.699e-06/2.335e-06/1.168e-06 over h=0.04/0.02/0.01 but remains
terminal-bridge-equivalent and no-span. Direct mean-acceleration bridge
correction worsens to 0.076159 or above and shifts the gap to `lie_position_u`.
A bilinear
active-velocity outer-product follow-up tests 24 target-free
feature/stage-2-velocity matrix rows; its best residual is only 0.898720 with
`stage2_velocity_feature_outer_stage2_velocity`, independent target rank 8, and
no span, excluding the tested component-pair coupling family. A componentwise
active-velocity diagonal follow-up tests 24 Hadamard/shifted-diagonal rows; its
best residual is only 0.898530 with
`stage2_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity`, again
rank 8/no span, excluding the tested row-local coupling family. The
nonlinear source-free final-stage velocity closure
then inserts those rows as 16 centered acceleration source-consistency rows
plus 8 final paper-stage velocity rows, solves 6 smooth/sharp trajectory rows
with max residual 9.49e-12 and raw terminal endpoint velocity 4.01e-16, and
uses no endpoint source, terminal-row replacement, or projection. Smooth/sharp
orders are 3.523/4.828 and 2.555/1.918, so terminal velocity is closed but
smooth position order still blocks full-TFE acceptance. A source-free
order/closure blend trajectory audit then tests beta=[0,0.5,1] over 18 rows:
beta=1 closes terminal velocity to 4.01e-16 but keeps smooth position order at
3.523, while beta=0/0.5 preserve smooth position order above 5 but leave
terminal velocity around 4e-6, so no tested beta satisfies both gates. The
nonlinear-history recurrent source-law screen tests five target-free norm,
Hadamard, bilinear, and second-difference history laws; all rows converge at
rank 132, but `terminal_closed_row_count=0`, `smooth_order_ok_count=0`, and
the best law has terminal velocity 1.954e-07 with min order 3.525, so this
source-law family is also ruled out. A
paper lower-pair
row-variant diagnostic then compares position-, velocity-, and
acceleration-level lower-pair row formulas over 18 one-step rows; all variants
solve with full rank 132 and max residual 7.286e-12, and
`acceleration_constraint` is best Schur-conditioned with max Schur condition
9.71e1 versus 5.98e3 for the position baseline. This is formulation evidence,
not an accepted full-TFE h-sweep. A paper lower-pair acceleration
terminal-output h-sweep diagnostic then runs the acceleration-level row over 6
smooth/sharp trajectory rows, with max terminal residual 8.35e-12, full rank
132, max raw/scaled conditions 4.37e8/5.83e3, smooth orders 4.937/4.799, and
sharp orders 2.555/1.918, while keeping `accepted_h_sweep_present=false` and
`full_tfe_stage_replacement=false`.
The paired paper lower-pair acceleration projection-dependence audit then
compares raw terminal paper output with endpoint-velocity-projected terminal
output over those same 6 rows. Raw/projected endpoint velocity residuals are
7.99e-06/9.66e-15, the max projection delta is 7.92e-06, and all 6 rows
require projection, so this branch is still not a projection-free full-TFE
replacement.
The paper lower-pair acceleration terminal-velocity closure diagnostic then
replaces only the final lower-pair acceleration rows with 8 weighted raw
terminal endpoint-velocity rows. It closes raw terminal velocity to 5.80e-16
without output projection, with max closure residual 9.73e-12, rank 132,
raw/scaled max conditions 1.28e10/7.99e4, smooth/sharp orders 3.459/4.838 and
2.555/1.918, and max replaced terminal lower-pair acceleration row 2.53e-4;
it remains diagnostic and keeps `full_tfe_stage_replacement=false`.
The terminal-row homotopy audit solves 30 one-step rows over
beta=[0,0.25,0.5,0.75,1], records max residual 6.22e-12, full rank 132,
raw/scaled max conditions 1.28e10/7.86e4, and beta0/beta1 terminal velocity
residuals 2.34e-10/1.29e-12, while still leaving full-TFE stage replacement
pending because beta=1 is terminal-row replacement.
The paper lower-pair terminal source-target audit records 6 case/h rows, maps
the 8 replaced terminal rows to 24 candidate stage-local lower-pair source rows
over the three paper stages, and keeps `full_tfe_stage_replacement=false`.
The paper lower-pair terminal source-lift audit records 6 case/h rows, lifts
that source into the same 24 stage-local lower-pair rows with
`sqrt(h*b_i)*terminal_lower_pair_source`, and verifies zero lift reconstruction
error plus max lift-ratio deviation 2.22e-16 while still keeping
`full_tfe_stage_replacement=false`.
The paper lower-pair terminal source-normalization audit records 6 case/h rows,
shows the raw budget source has max terminal reconstruction relative error
9.47e-1, and verifies
`terminal_lower_pair_source = terminal_row_vector/sqrt(h*b_terminal)` with zero
normalized reconstruction error while still keeping full-TFE stage replacement
pending.
The follow-up terminal source-insertion audit records 12 sign/case/h rows,
inserts the normalized source into the lower-pair Newton residual, converges all
12 one-step attempts, selects source_sign=-1, and records residuals from
4.00e-13 to 9.77e-12 while still keeping accepted h-sweep and full-TFE stage
replacement false.
The terminal source-insertion trajectory audit runs that best sign over
h=[0.04,0.02,0.01], completes all 6 smooth/sharp trajectory rows and all 28
source-ready/source-insertion steps with max source-insertion residual
9.75e-12, but the h=0.005 reference fails and raw terminal endpoint velocity
reaches 7.41. It is a quantified failure frontier rather than an accepted
h-sweep or full-TFE stage replacement.
The terminal source-insertion blow-up audit records 14 case/metric rows and 12
blow-up signals, with max mid-to-fine/coarse-to-fine ratios 7.339e3/4.936e5,
minimum observed h-power -9.456, and dominant signal
`cylindrical_smooth:max_normalized_source_norm`. It localizes the blocker to a
refinement-unstable closure-derived source policy while keeping full-TFE stage
replacement false.
The bounded-policy audit records the corresponding bounded-source target,
rejects the closure-derived source metrics, and shows that simple extra h^2
scaling is still insufficient for the dominant rows while keeping full-TFE
stage replacement false.
The stage-local bounded-source formula audit records 6 smooth/sharp case/h rows
and shows the local
`source_i = sqrt(h*b_i)*(terminal_lower_pair_row/sqrt(h*b_terminal))` formula is
bounded, with minimum local h-power 0.426, while the recurrent terminal-closure
source remains unbounded with minimum h-power -9.456, max recurrent/local
source ratio 1.003e6, and max raw terminal velocity 7.41. It keeps
`accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.

## Current Interpretation

The strongest current method is not just "higher order". The useful direction is:

```text
quaternion S^3 residual
+ AD/JAX Jacobian through friction and multipliers
+ Gauss6 for smooth friction
+ embedded Gauss64 adaptivity for sharp friction transitions
+ RATTLE-style projection as a practical endpoint-closure repair
+ PivotVA stage velocity/acceleration constraints as the best current non-projection full-DAE repair
+ FullVA off-axis stress test showing axis consistency is not the one-joint bottleneck
+ double-revolute interbody test showing PivotVA is not a one-body artifact
+ sparse/block Newton diagnostics showing solver scaling is now the visible bottleneck
+ CSR sparse Newton loop showing Gauss6 can be accelerated without changing trajectory
+ matrix-free Krylov diagnostic showing unpreconditioned GMRES is not enough
+ lagged sparse Newton diagnostic showing simple modified Newton is not enough
+ colored-JVP sparse AD diagnostic showing generic coloring is correct but not yet faster
+ batched colored-JVP sparse AD showing compiled coloring is faster than dense jacfwd on the 138D double-revolute residual
+ block-symbolic sparse pattern showing dense warm-up discovery is not required for correctness
+ JVP-pruned sparse pattern recovery showing the exact fine pattern can be obtained without dense Jacobians
+ cached sparse pattern reuse showing one discovered pattern can serve smooth and sharp longer-horizon runs
+ triple-revolute larger-topology scaling showing the sparse-AD path is not only a double-revolute artifact
+ generated block-dependency superset showing triple-revolute pruning no longer needs a full matrix superset
+ cache refresh/union showing missing sparse-pattern entries can be repaired without dense Jacobians
+ skew-axis parent-child revolute constraints showing the path is not limited to planar/global-axis joints
+ skew-axis prismatic lower-pair constraints showing the path is not limited to revolute joints
+ double-prismatic interbody constraints showing the prismatic test is not only a single-body slider
+ row-colored VJP showing the v044 color count can be reduced, but reverse-mode overhead still matters
+ true endpoint/velocity/acceleration or TFE algebraic treatment still to add
```

Compared with the paper's finite-difference TFE implementation, the local path is
better where the friction law is smooth because Gauss6 reaches near-sixth order
with JAX Jacobians and much lower error at similar cost. Compared with
trapezoidal/BDF2 baselines, it is much more accurate. Compared with reduced
Lobatto/TFE-style endpoint-node collocation, it is currently better on accuracy
per runtime. v024 further shows that direct Lobatto endpoint nodes fail on the
full absolute-coordinate revolute residual unless the full TFE/index-3 algebraic
treatment is added. v025 shows that endpoint projection is useful engineering:
it closes constraints and improves robustness, but it is not the same as a
high-order constrained residual. v026 moved pivot velocity consistency inside
the residual; v027 adds pivot acceleration consistency and reduces Gauss6
endpoint velocity drift to about 1e-12 without projection. v028 adds off-axis
torque and explicit hinge-axis consistency; it tightens axis diagnostics but
does not change the one-DOF trajectory. v029 moves to a two-body interbody
revolute chain and confirms the same PivotVA repair reduces endpoint velocity
drift by seven to eight orders, while exposing dense Newton cost as the next
engineering bottleneck. v030 diagnoses that bottleneck directly: the Gauss6
double-revolute Jacobians are about 3% dense, and sparse CSR linear solves are
orders faster than dense linear solves at the recorded 138-variable Newton
system size. v031 moves that sparse solve into the actual time integrator:
Gauss6 FullVA end-to-end runtime improves by 31.35x in the smooth targeted run
and 22.02x in the sharp targeted run, while the dense-vs-CSR final orientation
difference remains at roundoff scale. v032 tests the obvious matrix-free
extension. The JAX JVP is correct to roundoff, but unpreconditioned GMRES fails
after 200 iterations on the targeted Gauss6 FullVA systems, so plain
matrix-free Krylov is not the next best implementation. v033 tests a cheaper
modified-Newton compromise: reuse CSR Jacobians for two corrections or an
entire time step. It is numerically safe but not a useful speedup on this
small system, because extra Newton work offsets fewer Jacobian evaluations.
v034 implements the next structured-AD idea: column-colored JVP sparse Jacobian
assembly. It is correct to roundoff with a warm-up union sparsity pattern, but
is still slower than dense `jacfwd` on the 138-variable system because it uses
11 separate JVP calls per assembly. v035 batches those 11 color seeds into one
compiled `vmap(jvp)` dispatch. That changes the conclusion: smooth runtime is
0.038s versus dense `jacfwd` CSR 0.102s, and sharp runtime is 0.035s versus
dense 0.088s, while the dense-relative Jacobian error remains about
4.5e-18 and trajectory differences remain at roundoff scale.

The claim stops at true nonsmooth contact/stick-slip and at full production
index-3 DAE treatment. v023-v031 show the next bottleneck clearly: endpoint
velocity and acceleration constraints must be handled inside the
absolute-coordinate revolute solve, direct Lobatto nodes alone are not that
treatment, after-step projection is useful but accuracy-costing, and the first
successful in-residual repair now combines pivot velocity and pivot acceleration
consistency. v028 shows explicit hinge-axis consistency is possible but not the
remaining single-joint trajectory bottleneck. v029 shows the repair transfers
to an interbody joint. v030 shows the immediate computational target is
scalable sparse/block Newton linear algebra, ideally without first materializing
a dense AD Jacobian. v031 confirms sparse Newton solves are useful in the
actual loop. v032 shows matrix-free Newton-Krylov needs a preconditioner before
it is competitive. v033 shows simple Jacobian lagging is also not enough. The
v034-v035 sequence shows compiled colored sparse AD is now the best implemented
route for avoiding dense Jacobian materialization on the targeted system. v036
then removes the dense warm-up pattern dependency with a conservative
block-symbolic mask: it has zero missed dense entries and roundoff trajectory
agreement, but it is overconservative at 1755 entries and 34 colors. v037 uses
that safe block mask as a superset and prunes it by batched JVP dry-runs,
recovering the same 582-entry, 11-color pattern as dense warm-up discovery
without materializing dense Jacobians. v038 tests the first cache/reuse policy:
a pattern discovered once from the smooth short dry-run has zero missing entries
against T=0.12 dense validation for both smooth and sharp cases, and the cached
solver is 1.49x faster than dense `jacfwd` CSR in both longer runs. v039 moves
that question to a real larger topology: a three-body triple-revolute chain with
Brown-McPhee friction at all hinges and a 207-variable Gauss6 FullVA Newton
system. The JVP-pruned pattern has 930 entries and 11 colors, exactly matches
dense validation in both smooth and sharp cases, and gives 1.41x/1.67x runtime
speedups versus dense `jacfwd` CSR. v040 closes v039's main implementation
caveat by replacing the full superset with a generated block-dependency
superset. The superset has 2691 entries and 32 colors with zero dense-validation
misses; JVP pruning inside it recovers the exact 930-entry, 11-color dense
pattern and gives 2.14x/1.78x speedups versus dense `jacfwd` CSR. v041 adds
the cache policy: a smooth short cache transfers to longer nominal and
perturbed smooth/sharp cases with zero dense-validation misses, and a deliberate
stale-cache audit restores 23 removed entries through generated-block JVP
refresh. v042 then changes the lower-pair geometry itself: interbody revolute
axes are skew body-fixed axes, and each child proximal axis is constrained to
the parent body's distal axis. The generated block superset has zero dense
misses, pruning recovers the exact 2181-entry/31-color dense pattern, endpoint
velocity is around 1e-16, and sparse runtime is about 2x faster than dense
`jacfwd` CSR. v043 adds the first non-revolute lower-pair check: a skew-axis
prismatic residual with sliding friction. Its generated block superset has zero
dense-validation misses, JVP pruning recovers the exact 414-entry/18-color dense
pattern, and dense/sparse trajectories match exactly. It is not a speed win
because the 69D problem is too small for sparse-AD overhead to amortize. The
v044 test then moves the prismatic case to a two-body interbody chain. Its
generated block superset again has zero dense misses and JVP pruning recovers
the exact 2439-entry/90-color dense pattern with roundoff trajectory agreement.
The warmed runtime is not faster than dense `jacfwd`, which exposes the next
solver problem: the non-revolute interbody pattern needs much finer coloring or
block assembly. v045 tests one direct solver response: row-colored VJP lowers
the seed count from 90 to 54 on the same exact sparse pattern, but only ties or
slightly beats column-JVP and still loses to dense `jacfwd`. The next target is
component/block assembly or mixed revolute-prismatic/cylindrical joints where
the prismatic axis rotates with a moving parent.
