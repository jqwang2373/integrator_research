# D5 P_state PS2 Row-Injection Audit

Status: **PS2 row injection recorded; full PS2 remains open**.

This artifact records the 72-to-96 residual row injection used by the
weighted PS2 route. It is not a nonlinear PS2 inverse or inf-sup proof.

## Summary

- Row injection recorded: `True`.
- 72-to-96 row injection certified: `True`.
- Unweighted residual scaling certified: `True`.
- Row-selection operator 2-norm: `1.000000000000e+00`.
- Kinematic/lower-pair/non-dynamic rows: `72` / `24` / `96`.
- Full nonlinear mean-value binding certified: `False`.
- Full nonlinear PS2 certified: `False`.
- PS2 closed: `False`.
- Primitive/Taylor PC2 route closed: `False`.

## Operator Statement

`||Pi_kin delta N_h^nd||_2 <= ||delta N_h^nd||_2`

## Remaining Binding Gaps

- prove the nonlinear compact-tube mean-value estimate for the implemented rotational row eta_i - h sum_j A_ij J_r^{-1}(eta_j) omega_j

## Acceptance Boundary

- The 72-to-96 unweighted row injection is recorded.
- Nonlinear rotational-row mean-value binding remains open.
- PS2, PS3, P_state, PC2, and induced Taylor bounds remain open.
