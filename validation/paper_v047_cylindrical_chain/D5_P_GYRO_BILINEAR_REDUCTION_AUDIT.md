# D5 P_gyro Bilinear Reduction Audit

Status: **P_gyro bilinear reduction closed; primitive remains open**.

This read-only audit proves the algebraic Lipschitz reduction for the
body-frame gyroscopic map `G(omega)=omega x J omega`. It does not prove
the angular-velocity lift rate supplied by `P_state`, so it does not
close `P_gyro` or PC2.

## Summary

- Closed P_gyro subproofs: `3/3`.
- Open dependencies: `1`.
- Rotational Newton-Euler rows conditionally reduced: `18/18`.
- P_tube closed: `True`.
- P_state closed: `False`.
- P_gyro primitive closed: `False`.
- Primitive/Taylor PC2 route closed: `False`.

## Bound

For `G(omega)=omega x J omega`,

`G(omega_hat)-G(omega) = (omega_hat-omega) x J omega_hat + omega x J (omega_hat-omega)`.

On the compact proof tube, `||omega||, ||omega_hat|| <= M`, so

`||G(omega_hat)-G(omega)|| <= 2 M ||J|| ||omega_hat-omega||`.

Thus the gyroscopic term is `O(h^7)` once `P_state` proves the
angular-velocity lift `||omega_hat-omega|| = O(h^7)`.

## Conditional Row Corollary

Under the still-open `P_state` angular-velocity lift, the row-level
corollary in the manuscript gives

`C_gyro = 2 M_omega J_max C_omega`

and binds the estimate to rows

`[27, 28, 29, 33, 34, 35, 71, 72, 73, 77, 78, 79, 115, 116, 117, 121, 122, 123]`.

Conditional gyro row bounds under P_state: `18/18`.
Actual Taylor bounds proved by this audit remain `0`.

## Acceptance Boundary

- The constant-inertia compact-bound subproof is closed.
- The bilinear difference estimate is closed.
- The estimate is bound to the 18 rotational Newton-Euler rows.
- `P_state` remains open, so `P_gyro` remains open.
- Zero Taylor term bounds are certified by this audit.
- Primitive/Taylor PC2 lane remains open.
