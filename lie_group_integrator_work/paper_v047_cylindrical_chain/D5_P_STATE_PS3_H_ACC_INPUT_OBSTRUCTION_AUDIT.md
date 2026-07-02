# D5 P_state PS3 H-Acceleration Input Obstruction Audit

Status: **h-weighted acceleration input obstruction recorded; actual PS3 remains open**.

This read-only audit records why the current P_state PS3 evidence cannot
non-circularly supply the `h delta A` input required by the aggregate
weighted PS2 estimate.

## Summary

- State/acceleration/domain dimensions: `72` / `36` / `108`.
- Non-dynamic residual rows: `96`.
- Residual-only row deficit: `12`.
- Residual-only finite nullity range: `12`-`12`.
- Non-dynamic finite rank range: `96`-`96`.
- Weighted operator finite rank range: `108`-`108`.
- Weighted operator full column rank in probes: `True`.
- Residual-only input sufficient for h-acceleration: `False`.
- Independent h-weighted acceleration input closed: `False`.
- Actual PS3 state lift conversion closed: `False`.
- P_state primitive closed: `False`.
- Induced Taylor bounds proved: `0/162`.
- Primitive/Taylor PC2 route closed: `False`.

## Strict Obstruction

`||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)`.

The current 96 non-dynamic residual rows act on the 108-dimensional
`(S,A)` domain. At the recorded solved stages, `DN_h^nd` has rank
`96`, while `[DN_h^nd; hI_A]` has rank `108`. Thus the weighted
operator becomes full column rank only after the `h delta A` rows are
adjoined.

Velocity collocation gives

`delta_A = h^{-1} (A_G^{-1} \otimes I) (delta_V - rho_V)`.

That identity uses `delta_V`, which is a component of the `P_state`
unknown. It is therefore circular as an independent PS3 input for
proving the `P_state` lift.

## Acceptance Boundary

- This audit does not prove a theorem-level independent h-acceleration input.
- The finite rank probe is diagnostic evidence, not a proof.
- Actual PS3 remains open.
- `P_state` remains open.
- Primitive/Taylor PC2 lane remains open.

## Strict Close Route

The recommended non-circular close route is the full 132-row dynamic
residual route: prove the D5 lifted-stage dynamic defect for the 36
Newton-Euler rows by row-local Taylor expansion, then apply the full
stage-residual perturbation criterion. This route would control the
missing dynamic/free directions directly instead of asking the
96-row residual-only map to supply `h delta A`.

Two other routes remain possible but are not closed: prove
`delta_V=O(h^8)` and `rho_V=O(h^8)` before the `A_G^{-1}/h` inversion,
or weaken the theorem by stating the independent h-weighted
acceleration input as an explicit assumption.
