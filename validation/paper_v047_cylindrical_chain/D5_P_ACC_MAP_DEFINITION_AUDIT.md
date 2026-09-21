# D5 P_acc Map Definition Audit

Status: **P_acc map definition closed; lift remains open**.

This read-only audit closes only PA1 for `P_acc`: the accepted
translational and angular acceleration variables are bound to the 36
D5 acceleration-lift Taylor rows. It does not prove an `O(h^7)`
acceleration lift rate.

## Summary

- Closed P_acc subproofs: `1/4`.
- Open P_acc subproofs: `3`.
- Acceleration-map rows: `36/36`.
- Translational/angular acceleration rows: `18/18`.
- P_acc primitive closed: `False`.
- Acceleration lift rate proved: `False`.
- Primitive/Taylor PC2 route closed: `False`.

## Map Interface

`A_h^acc(A)` binds `A=(a_i, alpha_i)` to the accepted acceleration
lift terms `T_acceleration_lift` and `R_angular_acceleration_lift`.

| term family | rows |
|---|---:|
| `T_acceleration_lift` | `18` |
| `R_angular_acceleration_lift` | `18` |

## Acceptance Boundary

- PA1 map definition is closed.
- PA2 velocity-collocation-to-acceleration lift proof remains open.
- PA3 independence from dynamic balance remains open.
- PA4 residual-ordering/Taylor-term binding proof remains open.
- `P_acc` remains open.
- Primitive/Taylor PC2 lane remains open.
