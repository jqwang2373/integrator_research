# D5 P_acc Independence Audit

Status: **P_acc independence closed; lift remains open**.

This read-only audit closes only PA3 for `P_acc`: the proof route for
the acceleration-lift primitive is restricted to non-dynamic FullVA
row families and excludes Newton-Euler weak-balance rows as inputs.
It does not prove an `O(h^7)` acceleration lift rate.

## Summary

- Closed P_acc subproofs after independence: `3/4`.
- Open P_acc subproofs after independence: `1`.
- Non-dynamic input families certified: `3/3`.
- Dynamic-balance input families used: `0`.
- Dynamic-balance rows disallowed as inputs: `36`.
- P_acc primitive closed: `False`.
- Acceleration lift rate proved: `False`.
- Taylor bounds proved: `0/36`.
- Primitive/Taylor PC2 route closed: `False`.

## Non-Dynamic Input Boundary

| family | offset | width | rows | certified |
|---|---:|---:|---:|---:|
| `translational_velocity_weak_defect` | `12` | `6` | `18` | `True` |
| `angular_velocity_weak_defect` | `18` | `6` | `18` | `True` |
| `lower_pair_index3_weak_constraints` | `36` | `8` | `24` | `True` |

The Newton-Euler weak-balance family is present at offset `24` with
width `12`, but it is excluded from the 96-row certificate and is not
used as a `P_acc` independence input.

## Acceptance Boundary

- PA1 map definition is closed.
- PA3 lower-pair acceleration independence from dynamic balance is closed.
- PA4 row-ordering/Taylor-term binding is closed.
- PA2 velocity-collocation-to-acceleration lift proof remains open.
- `P_acc` remains open.
- Primitive/Taylor PC2 lane remains open.
