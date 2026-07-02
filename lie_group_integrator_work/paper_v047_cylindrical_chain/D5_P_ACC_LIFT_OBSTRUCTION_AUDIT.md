# D5 P_acc PA2 Lift-Obstruction Audit

Status: **PA2 obstruction recorded; P_acc lift remains open**.

This read-only audit records a narrow anti-overclaim result. The
velocity-collocation rows alone are insufficient to prove the
unweighted `O(h^7)` acceleration lift required by the current D5
Taylor budget.

## Summary

- PA2 closed: `False`.
- P_acc primitive closed: `False`.
- Velocity-collocation alone sufficient for O(h^7) acceleration: `False`.
- Current recorded inputs imply only: `O(h^6)`.
- Acceleration lift rate proved: `False`.
- Taylor bounds proved: `0/36`.
- Primitive/Taylor PC2 route closed: `False`.

## Rate Algebra

For the translational and angular velocity-collocation rows, subtracting
the lifted Gauss equation from the accepted stage equation gives

`delta_V - h (A_G \otimes I) delta_A = rho_V`.

Since the three-stage Gauss matrix is invertible,

`delta_A = h^{-1} (A_G^{-1} \otimes I) (delta_V - rho_V)`.

The audited Gauss matrix has determinant `8.333333e-03` and
`||A_G^-1||_inf=2.432796e+01`, so the inverse is uniformly bounded
but the factor `1/h` is unavoidable. Thus `delta_V=O(h^7)` and
`rho_V=O(h^7)` imply only `delta_A=O(h^6)` in the unweighted norm.

## Correct PA2 Close Conditions

- prove `delta_V=O(h^8)` and `rho_V=O(h^8)` before applying `A_G^{-1}/h`;
- or prove an independent non-dynamic stage-map inverse that controls acceleration directly;
- or keep `P_acceleration_lift=O(h^7)` as an explicit theorem assumption.

## External TFE Scaling Context (Diagnostic Only)

The source-paper TFE formulas provide diagnostic scaling context for
derivative reconstruction through step-size-dependent operators.
Its first-order example records inverse-step derivative scaling for
`delta v` and `delta vdot`, and its higher-order relations reconstruct
`y` and `z` through derivative coefficient matrices. This supports the
PA2 obstruction rather than closing it: those formulas do not prove the
unweighted `delta A=O(h^7)` estimate required by the separate
primitive/Taylor acceleration-lift rows.

## Runtime Row-Scaling Evidence

The accepted `run_v047.py` residual has the same scaling obstruction.
The velocity-collocation rows contain acceleration through `h A_G`,
while the Newton-Euler rows use `m_b a` and `J_b alpha` without an
extra factor of `h`. The lower-pair acceleration constraints are
non-dynamic and unweighted, but they only constrain lower-pair
constraint directions and do not form a full unweighted inverse for
all body acceleration components required by the 36 Newton-Euler
Taylor terms.

## Acceptance Boundary

- This audit sharpens PA2; it does not close PA2.
- `P_acc` remains open.
- Zero P_acc-induced Taylor bounds are certified.
- Primitive/Taylor PC2 lane remains open.
