# D5 P_state PS2 Weighted Target Audit

Status: **PS2 target specified; P_state lift remains open**.

This read-only audit fixes the correct PS2 inverse/inf-sup target.
The non-dynamic map is not a literal square inverse in all state and
acceleration variables; the acceleration block must enter as a
parameter in the `h`-weighted norm.

## Summary

- PS2 target specification closed: `True`.
- PS2 inverse or inf-sup closed: `False`.
- PS3 state lift conversion closed: `False`.
- P_state primitive closed: `False`.
- State block dimension: `72`.
- Auxiliary acceleration dimension: `36`.
- Non-dynamic row dimension: `96`.
- Induced Taylor bounds proved: `0/162`.
- Primitive/Taylor PC2 route closed: `False`.

## Weighted PS2 Target

`||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)`.

The full `(S,A)` map has `108` coordinates and `96` residual rows,
so a literal square inverse in all variables is not the PS2 target.
With acceleration treated as a parameter, PS2 must prove a uniform
state-block inf-sup bound on the compact proof tube.

## Acceptance Boundary

- The PS2 target specification is closed.
- The uniform PS2 inf-sup constant remains open.
- PS3 conversion to `O(h^7)` state lift rates remains open.
- `P_state` remains open.
- Primitive/Taylor PC2 lane remains open.
