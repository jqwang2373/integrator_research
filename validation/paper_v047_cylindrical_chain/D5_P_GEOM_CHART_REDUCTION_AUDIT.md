# D5 P_geom Chart Reduction Audit

Status: **P_geom chart reduction closed; primitive remains open**.

This read-only audit proves the accepted-chart Lipschitz reduction for
the lower-pair multiplier-wrench geometry maps `G_b(q)^T lambda` and
`H_b(q)^T lambda`. It does not prove the pose or multiplier lift rates,
so it does not close `P_geom` or PC2.

## Summary

- Closed P_geom subproofs: `3/4`.
- Open dependencies: `2`.
- Multiplier-geometry rows conditionally reduced: `36/36`.
- Translational/rotational rows: `18/18`.
- P_tube closed: `True`.
- P_state closed: `False`.
- P_lambda closed: `False`.
- P_geom primitive closed: `False`.
- Primitive/Taylor PC2 route closed: `False`.

## Bound

For `A(q)` equal to either `G_b(q)` or `H_b(q)`,

`A(q_hat)^T lambda_hat - A(q)^T lambda = (A(q_hat)-A(q))^T lambda_hat + A(q)^T (lambda_hat-lambda)`.

On the compact proof tube, bounded `A`, bounded `D A`, and bounded
`lambda_hat` give

`||A(q_hat)^T lambda_hat - A(q)^T lambda|| <= C_A (||q_hat-q|| + ||lambda_hat-lambda||)`.

Thus the geometry contribution is `O(h^7)` once `P_state` supplies the
pose lift and `P_lambda` supplies the multiplier lift.

## Conditional Row Corollary

Under the still-open `P_state` pose lift and `P_lambda` multiplier
lift, the row-level corollary in the manuscript gives

`C_geom = C_max (C_q + C_lambda)`

and binds the estimate to rows

`[24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123]`.

Conditional geometry row bounds under lifts: `36/36`.
Actual Taylor bounds proved by this audit remain `0`.

## Acceptance Boundary

- The accepted-chart geometry expansion is closed.
- The compact-tube Lipschitz reduction is closed.
- The estimate is bound to the 36 multiplier-geometry term rows.
- `P_state` and `P_lambda` remain open, so `P_geom` remains open.
- Zero Taylor term bounds are certified by this audit.
- Primitive/Taylor PC2 lane remains open.
