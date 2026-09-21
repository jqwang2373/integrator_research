# D5 P_lambda Interface Audit

Status: **P_lambda interface closed; lift remains open**.

This read-only audit closes only PL1 for `P_lambda`: the lower-pair
multiplier variables and their KKT/Newton-Euler column interface are
exposed in the accepted residual. It does not prove an `O(h^7)`
multiplier lift rate, a uniform inf-sup bound, any Taylor bound, or PC2.

## Summary

- Closed P_lambda subproofs after interface: `1/4`.
- Open P_lambda subproofs after interface: `3`.
- Stage lambda variables: `24`.
- Per-stage lambda variables: `8`.
- Direct multiplier-wrench term rows: `36`.
- Primitive-ledger term rows using P_lambda: `72`.
- P_lambda primitive closed: `False`.
- Multiplier lift rate proved: `False`.
- Uniform inf-sup bound proved: `False`.
- Taylor bounds proved: `0/72`.
- Primitive/Taylor PC2 route closed: `False`.

## Multiplier Interface

| item | value |
|---|---:|
| stages | `3` |
| joints | `2` |
| lambda size per joint | `4` |
| per-stage lambda dimension | `8` |
| total lambda variables | `24` |

The first two multiplier components define the normal force in the
joint basis. The last two components define the axis/twist torque
multipliers. The multiplier-lift Taylor rows are the 36 rows named
`T_multiplier_force_lift` and `R_multiplier_torque_lift`; the
primitive-reduction ledger records 72 total D5 term rows depending on
`P_multiplier_lift`.

## Acceptance Boundary

- PL1 multiplier variable and KKT-column interface is closed.
- PL2/PL3/PL4 are not closed by this interface audit; later audits record PL2, PL3, and conditional PL4 separately.
- The actual multiplier lift rate still waits on the `P_state` and `P_acc` inputs.
- `P_lambda` remains open.
- Primitive/Taylor PC2 lane remains open.
