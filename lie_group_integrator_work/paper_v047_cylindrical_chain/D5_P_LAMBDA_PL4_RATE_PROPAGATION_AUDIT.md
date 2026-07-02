# D5 P_lambda PL4 Rate Propagation Audit

Status: **PL4 conditional multiplier-rate propagation closed; P_lambda remains open**.

This read-only audit proves the conditional propagation step from
state and acceleration lift errors to the lower-pair multiplier error.
It uses the PL2 compact-tube inf-sup bound and a first-order Taylor
expansion with quadratic remainder. It does not prove the required
state or acceleration lift inputs, so it does not close `P_lambda` or PC2.

## Summary

- P_lambda subproofs closed: `4/4`.
- Open input dependencies: `2`.
- Direct multiplier rows: `36/36`.
- Term rows using P_lambda: `72/72`.
- PL2 uniform inf-sup proved: `True`.
- Conditional multiplier lift rate proved: `True`.
- Actual multiplier lift rate proved: `False`.
- P_state actual state lift input closed: `False`.
- P_acc unweighted acceleration lift input closed: `False`.
- P_lambda primitive closed: `False`.
- Taylor term bounds proved: `0`.
- Primitive/Taylor PC2 route closed: `False`.
- Reader-facing conditional nonclosure lemma main/flat: `True/True`.

## Taylor Propagation

Let `F(y,lambda,h)` be the accepted lower-pair dynamic-row map, with
`y` collecting the state and acceleration variables.  On the compact
proof tube, PL2 gives

`||B(y,lambda,h) delta_lambda|| >= gamma_PL2 ||delta_lambda||`.

For two points on the same accepted lower-pair solution branch,

`0 = B delta_lambda + D_y F delta_y + O((||delta_y||+||delta_lambda||)^2)`.

The compact `C^2` bounds and the PL2 left inverse absorb the quadratic
remainder for sufficiently small `h`, giving

`||delta_lambda|| <= C_lambda_y (||delta_z|| + ||delta_a||)`.

Thus `delta_lambda=O(h^7)` once `P_state` supplies `delta_z=O(h^7)`
and `P_acc` supplies the unweighted acceleration lift `delta_a=O(h^7)`.

## Acceptance Boundary

- PL4 is closed as a conditional Taylor/implicit-function propagation.
- `P_state` and `P_acc` input lifts remain open.
- The actual multiplier lift rate remains open.
- The reader-facing PL4 nonclosure lemma records that `4/4` local PL subproofs mean conditional propagation only, not actual `P_lambda` closure.
- Zero Taylor term bounds are certified by this audit.
- Primitive/Taylor PC2 lane remains open.
