# D5 Primitive-Bound Reduction Audit

Status: **primitive reduction recorded; primitive/Taylor PC2 route remains open**.

This read-only audit groups the 162 D5 Taylor subterms by the primitive
stage-bound obligations that would imply their O(h^7) bounds. It does
close only the compact-tube primitive; it does not prove the five
lift and bilinear primitives and does not close the optional
primitive/Taylor PC2 route; the active direct-route theorem bridge is
closed elsewhere.

## Summary

- Taylor subterms with reduction rules: `162/162`.
- Primitive obligations: `6`.
- Primitive obligations proved: `1/6`.
- P_tube compact constants closed: `True`.
- Taylor term bounds proved: `0/162`.
- Separate primitive/Taylor PC2 route closed: `False`.

## Reduction Groups

| group | term rows | role |
|---|---:|---|
| `acceleration_lift` | `36` | translational and angular acceleration lift errors |
| `smooth_force_torque_lift` | `72` | smooth force, torque, and friction maps on the proof tube |
| `multiplier_geometry_lift` | `36` | multiplier and dynamic-row geometry/Jacobian lifts |
| `gyroscopic_bilinear_lift` | `18` | body-frame angular-velocity bilinear term |

## Conditional Row-Level Corollaries

- Smooth force/torque/friction corollary present main/flat: `True/True`.
- Smooth force/torque/friction rows conditionally bounded: `72/72`.
- Smooth force/torque/friction actual Taylor bounds proved: `0/72`.
- D4 direct-route smoothness used as primitive-rate proof: `False`.

## Primitive Obligations

| id | term rows | proved | statement |
|---|---:|---:|---|
| `P_state_lift` | `126` | `False` | stage pose, translational velocity, and angular velocity lift errors are O(h^7) |
| `P_acceleration_lift` | `36` | `False` | stage translational and angular acceleration lift errors are O(h^7) |
| `P_multiplier_lift` | `72` | `False` | stage lower-pair multiplier lift errors are O(h^7) |
| `P_geometry_lift` | `36` | `False` | dynamic-row force and torque Jacobian lift errors are O(h^7) |
| `P_gyroscopic_lift` | `18` | `False` | body-frame gyroscopic bilinear lift errors are O(h^7) |
| `P_uniform_tube_constants` | `162` | `True` | all reduction constants are uniform on the compact smooth proof tube |

## Acceptance Boundary

- All 162 Taylor subterms have a recorded reduction rule.
- The compact-tube primitive obligation is proved.
- Five lift and bilinear primitive obligations remain open.
- Zero Taylor term bounds are certified.
- The primitive/Taylor PC2 route remains open until the primitive bounds and every induced term bound are proved uniformly.
