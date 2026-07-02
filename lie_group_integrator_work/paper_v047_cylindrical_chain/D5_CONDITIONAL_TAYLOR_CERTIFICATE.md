# D5 Conditional Taylor Certificate

Status: **conditional Taylor certificate recorded; primitive-and-Taylor PC2 route remains open**.
Here `submission_ready=false` is scoped to the conditional Taylor/global proof-package boundary,
not to the separate narrowed-claim package decision.

This read-only certificate checks the finite implication from the D5
primitive obligations to the 162 Newton-Euler Taylor subterms. It is
conditional on the five open lift/bilinear primitives and does not
prove those primitives, certify an actual Taylor bound, or close the primitive/Taylor PC2 route.

## Summary

- Dynamic rows conditionally covered: `36/36`.
- Taylor subterms conditionally covered: `162/162`.
- Actual Taylor bounds proved: `0/162`.
- Open primitive assumptions: `5`.
- Proved primitive obligations used: `1`.
- Primitive/Taylor PC2 route closed: `False`.
- Conditional templates are additive proof evidence: `False`.
- Conditional templates spliced with direct PC2 bridge: `False`.
- Finite-sum row constant recorded: `True`.
- Finite-sum step is inverse projection from aggregate residual: `False`.
- Primitive route must prove five lift primitives and redo the perturbation chain: `True`.
- Reference proof imports Taylor estimate: `False`.
- Reference proof supplies primitive FullVA lift estimate: `False`.
- Reference proof closes primitive/Taylor ledger or PC2: `False/False`.
- Submission ready: `False`.
- Submission-ready scope: `d5_conditional_taylor_global_boundary_not_narrowed_claim_package_decision`.
- Conditional Taylor certificate scope: `conditional_162_subterm_implication_under_open_primitives_not_actual_taylor_bound_closure`.
- Remaining global submission boundaries: `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.

## Primitive Usage

| primitive | term rows | proved now | assumed now |
|---|---:|---:|---:|
| `P_acceleration_lift` | `36` | `False` | `True` |
| `P_geometry_lift` | `36` | `False` | `True` |
| `P_gyroscopic_lift` | `18` | `False` | `True` |
| `P_multiplier_lift` | `72` | `False` | `True` |
| `P_state_lift` | `126` | `False` | `True` |
| `P_uniform_tube_constants` | `162` | `True` | `False` |

## Reduction Groups

| group | term rows |
|---|---:|
| `acceleration_lift` | `36` |
| `gyroscopic_bilinear_lift` | `18` |
| `multiplier_geometry_lift` | `36` |
| `smooth_force_torque_lift` | `72` |

## Primitive/Taylor Diagnostic Templates

| group | template | bound |
|---|---|---|
| `acceleration_lift` | `exact_linear_no_remainder` | `||L(Ahat)-L(A)|| <= C_acc ||delta A|| = O(h^7) under P_acceleration_lift` |
| `gyroscopic_bilinear_lift` | `exact_bilinear_difference` | `||delta(omega x J omega)|| <= C_gyro ||delta omega|| = O(h^7) under P_state_lift` |
| `multiplier_geometry_lift` | `product_taylor_mean_value` | `||delta(A^T lambda)|| <= C_A (||delta q||+||delta lambda||) = O(h^7) under P_state_lift and P_multiplier_lift` |
| `smooth_force_torque_lift` | `first_order_taylor_integral_remainder` | `||F(zhat)-F(z)|| <= L_F ||delta z|| = O(h^7) under P_state_lift and, where present, P_multiplier_lift` |

## Row Coverage

| row | block | terms | conditional terms | actual terms proved |
|---:|---|---:|---:|---:|
| `24` | `translational_newton_balance` | `4` | `4` | `0` |
| `25` | `translational_newton_balance` | `4` | `4` | `0` |
| `26` | `translational_newton_balance` | `4` | `4` | `0` |
| `27` | `rotational_euler_balance` | `5` | `5` | `0` |
| `28` | `rotational_euler_balance` | `5` | `5` | `0` |
| `29` | `rotational_euler_balance` | `5` | `5` | `0` |
| `30` | `translational_newton_balance` | `4` | `4` | `0` |
| `31` | `translational_newton_balance` | `4` | `4` | `0` |
| `32` | `translational_newton_balance` | `4` | `4` | `0` |
| `33` | `rotational_euler_balance` | `5` | `5` | `0` |
| `34` | `rotational_euler_balance` | `5` | `5` | `0` |
| `35` | `rotational_euler_balance` | `5` | `5` | `0` |
| `68` | `translational_newton_balance` | `4` | `4` | `0` |
| `69` | `translational_newton_balance` | `4` | `4` | `0` |
| `70` | `translational_newton_balance` | `4` | `4` | `0` |
| `71` | `rotational_euler_balance` | `5` | `5` | `0` |
| `72` | `rotational_euler_balance` | `5` | `5` | `0` |
| `73` | `rotational_euler_balance` | `5` | `5` | `0` |
| `74` | `translational_newton_balance` | `4` | `4` | `0` |
| `75` | `translational_newton_balance` | `4` | `4` | `0` |
| `76` | `translational_newton_balance` | `4` | `4` | `0` |
| `77` | `rotational_euler_balance` | `5` | `5` | `0` |
| `78` | `rotational_euler_balance` | `5` | `5` | `0` |
| `79` | `rotational_euler_balance` | `5` | `5` | `0` |
| `112` | `translational_newton_balance` | `4` | `4` | `0` |
| `113` | `translational_newton_balance` | `4` | `4` | `0` |
| `114` | `translational_newton_balance` | `4` | `4` | `0` |
| `115` | `rotational_euler_balance` | `5` | `5` | `0` |
| `116` | `rotational_euler_balance` | `5` | `5` | `0` |
| `117` | `rotational_euler_balance` | `5` | `5` | `0` |
| `118` | `translational_newton_balance` | `4` | `4` | `0` |
| `119` | `translational_newton_balance` | `4` | `4` | `0` |
| `120` | `translational_newton_balance` | `4` | `4` | `0` |
| `121` | `rotational_euler_balance` | `5` | `5` | `0` |
| `122` | `rotational_euler_balance` | `5` | `5` | `0` |
| `123` | `rotational_euler_balance` | `5` | `5` | `0` |

## Acceptance Boundary

- This certificate proves only a finite conditional implication.
- It assumes the five open primitive obligations: state and acceleration root lifts, the multiplier lift propagated from them, and the downstream geometry and gyroscopic reductions.
- It does not certify any actual D5 Taylor subterm bound.
- The Wieloch--Arnold constrained-BDF proof (`wieloch2021bdf`; local reference text `../../1-s2.0-S0377042719305229-main.txt`) is invoked as proof-order discipline only; it does not import a Taylor estimate, primitive FullVA lift, multiplier recursion, hidden-constraint estimate, or PC2 input for this certificate.
- The conditional templates are not additive proof evidence and cannot be spliced with the direct PC2 bridge.
- A primitive-route theorem would have to prove the five open primitive obligations and redo the residual-to-root, endpoint, solver, and global-transfer chain.
- It does not close the primitive-route proof gap or submission readiness; only the active direct PC2 residual-bridge proof-gap slot is closed elsewhere by the direct residual-bridge route.
