# D5 P_state PS2 Aggregate Promotion Audit

Status: **aggregate weighted PS2 inverse closed; P_state remains open**.

This artifact combines the weighted target, kinematic subblock, SO(3)
chart binding, 72-to-96 row injection, and nonlinear rotational-row
binding into one compact-tube PS2 estimate. It does not instantiate PS3.

## Summary

- Aggregate promotion recorded: `True`.
- Aggregate weighted PS2 inverse certified: `True`.
- Uniform PS2 constant certified: `True`.
- PS2 inverse or inf-sup closed: `True`.
- Actual PS3 state lift conversion closed: `False`.
- P_state primitive closed: `False`.
- Primitive/Taylor PC2 route closed: `False`.

## Aggregate Estimate

`||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)`.

The 72 kinematic rows control the state block in the accepted Lie chart,
the nonlinear rotational row is absorbed by the compact-tube mean-value
estimate, and the 72-to-96 selector has norm one, so the full
non-dynamic residual norm dominates the selected kinematic residual.

## Acceptance Boundary

- The uniform weighted PS2 inverse is closed.
- The finite linearization probe remains diagnostic, not a theorem input.
- This audit does not instantiate PS3.
- P_state, PC2, and induced Taylor bounds remain open.
