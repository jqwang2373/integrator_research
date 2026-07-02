# D5 Taylor Term-Budget Audit

Status: **D5 Taylor subterm budget recorded; separate primitive-route certificate remains open**.
Here `submission_ready=false` is scoped to the primitive Taylor/global proof-package boundary,
not to the separate narrowed-claim package decision.

This read-only audit decomposes the open lifted-stage Newton-Euler
dynamic term into row-local Taylor subterms. It does not certify any
subterm bound and does not close the separate primitive/Taylor reproof
route; it is not used by the active direct-route conditional theorem proof.

## Summary

- Dynamic rows: `36/36`.
- Translational/rotational rows: `18/18`.
- Translational subterms per row: `4`.
- Rotational subterms per row: `5`.
- Total Taylor subterms: `162`.
- Regularity-ready subterms: `162/162`.
- Row-binding-ready subterms: `162/162`.
- Primitive/Taylor reduction subterms: `162/162`.
- Anti-circular Taylor subterms: `162/162`.
- Subterms blocked by open primitives: `162/162`.
- Unweighted acceleration-blocked subterms: `36/36`.
- h-weighted acceleration sufficient subterms: `0`.
- Certified Taylor-bound subterms: `0/162`.
- Open Taylor-bound subterms: `162/162`.
- Separate primitive/Taylor PC2 route closed: `False`.
- Submission ready: `False`.
- Submission-ready scope: `d5_primitive_taylor_term_budget_global_boundary_not_narrowed_claim_package_decision`.
- Primitive Taylor budget scope: `162_subterm_budget_inventory_not_actual_taylor_bound_closure`.
- Remaining global submission boundaries: `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.

## Term Templates

| block | term | expression | required bound | proof status |
|---|---|---|---|---|
| translational | `T_acceleration_lift` | `m_b (a_hat_{s,b} - a_b(t_s))` | `O(h^7)` | conditional `linear_unweighted_acceleration_lift`; open |
| translational | `T_external_force_lift` | `f_ext(q_hat_s,v_hat_s,t_s) - f_ext(q(t_s),v(t_s),t_s)` | `O(h^7)` | conditional `smooth_force_lipschitz_state_lift`; open |
| translational | `T_multiplier_force_lift` | `G_hat_{s,b}^T lambda_hat_s - G_b(q(t_s))^T lambda(t_s)` | `O(h^7)` | conditional `product_geometry_multiplier_lift`; open |
| translational | `T_friction_force_lift` | `f_fric(q_hat_s,v_hat_s,lambda_hat_s) - f_fric(q(t_s),v(t_s),lambda(t_s))` | `O(h^7)` | conditional `smooth_friction_lipschitz_state_multiplier_lift`; open |
| rotational | `R_angular_acceleration_lift` | `J_b (alpha_hat_{s,b} - alpha_b(t_s))` | `O(h^7)` | conditional `linear_unweighted_angular_acceleration_lift`; open |
| rotational | `R_gyroscopic_lift` | `omega_hat_{s,b} x J_b omega_hat_{s,b} - omega_b(t_s) x J_b omega_b(t_s)` | `O(h^7)` | conditional `bilinear_gyroscopic_mean_value_lift`; open |
| rotational | `R_external_torque_lift` | `tau_ext(q_hat_s,v_hat_s,t_s) - tau_ext(q(t_s),v(t_s),t_s)` | `O(h^7)` | conditional `smooth_torque_lipschitz_state_lift`; open |
| rotational | `R_multiplier_torque_lift` | `H_hat_{s,b}^T lambda_hat_s - H_b(q(t_s))^T lambda(t_s)` | `O(h^7)` | conditional `product_geometry_multiplier_lift`; open |
| rotational | `R_friction_torque_lift` | `tau_fric(q_hat_s,v_hat_s,lambda_hat_s) - tau_fric(q(t_s),v(t_s),lambda(t_s))` | `O(h^7)` | conditional `smooth_friction_torque_lipschitz_state_multiplier_lift`; open |

## Primitive/Taylor Diagnostic Boundary

- Every subterm has a recorded Taylor/mean-value inequality and primitive dependency list.
- The primitive/Taylor reductions use compact-tube smoothness and row binding only.
- They do not use Lemma `stage-residual-defect`, D5 direct substitution, finite probes, or residual-to-error promotion.
- The 36 acceleration subterms remain blocked because the implemented Newton-Euler rows are unweighted.
- Recorded `h delta A` control is not sufficient for the unweighted acceleration Taylor subterms.

## P_acc Primitive/Taylor Requirement

- Acceleration Taylor subterms: `36`.
- Translational acceleration subterms: `18`.
- Rotational acceleration subterms: `18`.
- Required primitive input: unweighted `||delta A||=O(h^7)`.
- Velocity-collocation alone currently gives only unweighted `O(h^6)`.
- The recorded weighted diagnostic controls `h delta A`, not the unweighted D5 acceleration terms.

The acceleration reductions are exact linear Taylor reductions:
`||m_b delta a|| <= m_max ||delta a||` and
`||J_b delta alpha|| <= J_max ||delta alpha||`. Since the
implemented Newton-Euler rows contain these acceleration terms without
an extra factor of `h`, `h delta A=O(h^7)` cannot certify the required
unweighted `O(h^7)` Taylor subterm bounds.

## Acceptance Boundary

- Finite probes are not sufficient for any subterm.
- Residual-to-error promotion is not allowed for any subterm.
- Primitive/Taylor PC2 route closes only after all 162 Taylor subterms have independent uniform O(h^7) bounds.
