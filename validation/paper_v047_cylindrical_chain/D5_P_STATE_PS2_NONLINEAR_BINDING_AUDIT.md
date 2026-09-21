# D5 P_state PS2 Nonlinear Binding Audit

Status: **PS2 nonlinear rotational-row binding closed; aggregate PS2 promotion remains open**.

This artifact records the compact-tube mean-value estimate for the
implemented rotational Lie-collocation row used by the weighted PS2
route. It is a component proof, not a standalone PS2 inverse proof.

## Summary

- Nonlinear binding recorded: `True`.
- Rotational Lie-row mean-value binding certified: `True`.
- Compact-tube Lipschitz bound certified: `True`.
- Small-step absorption certified: `True`.
- Full nonlinear mean-value binding certified: `True`.
- Full nonlinear PS2 certified by this artifact: `False`.
- PS2 closed: `False`.
- Primitive/Taylor PC2 route closed: `False`.

## Mean-Value Bound

`F(eta, omega) = J_r(eta)^(-1) omega` is smooth on the accepted compact
chart tube. Hence `||Delta F|| <= L_F (||Delta eta|| + ||Delta omega||)`.

For the implemented row

`R_eta_i = eta_i - h sum_j A_ij J_r(eta_j)^(-1) omega_j`,

the perturbation term is multiplied by `h ||A_G||_2`. After shrinking the
asymptotic step threshold so that `h ||A_G||_2 L_F <= 1/2`, the nonlinear
term is absorbed on the left, giving the rotational weighted-PS2 bound.

## Remaining Promotion Gap

- promote the component nonlinear binding together with the kinematic-block, Lie-chart, and row-injection certificates into the aggregate weighted PS2 inverse constant

## Acceptance Boundary

- The rotational nonlinear compact-tube mean-value estimate is certified.
- The component proof uses only the non-dynamic map, Lie chart, and compact-tube constants.
- It does not by itself promote the aggregate PS2 inverse.
- PS3, P_state, PC2, and induced Taylor bounds remain open.
