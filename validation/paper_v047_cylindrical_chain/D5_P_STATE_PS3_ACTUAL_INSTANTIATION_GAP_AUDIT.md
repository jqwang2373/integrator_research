# D5 P_state PS3 Actual-Instantiation Gap Audit

Status: **actual PS3 instantiation gap recorded; P_state remains open**.

This read-only audit narrows the post-aggregate-PS2 gap. The aggregate
weighted PS2 inverse is closed, and the 96-row non-dynamic residual
certificate is available. The remaining PS3 blocker is an independent
h-weighted acceleration input that does not reuse the state-lift
variable being solved for.

## Summary

- Input requirements closed: `2/4`.
- PS2 dependency satisfied by aggregate: `True`.
- Non-dynamic residual certificate available: `True`.
- H-acceleration input obstruction recorded/nullity/residual-only sufficient: `True` / `12`-`12` / `False`.
- Independent h-weighted acceleration input closed: `False`.
- Non-circular PS3 instantiation closed: `False`.
- Actual PS3 state lift conversion closed: `False`.
- P_state primitive closed: `False`.
- Induced Taylor bounds proved: `0/162`.
- Primitive/Taylor PC2 route closed: `False`.

## Input Requirements

| id | status | statement |
|---|---|---|
| `PS3-I1` | `True` | Aggregate weighted PS2 inverse on the compact proof tube. |
| `PS3-I2` | `True` | Non-dynamic residual defect source for the 96 certified rows. |
| `PS3-I3` | `False` | Independent h-weighted acceleration input for PS3 that does not use the state-lift variable being solved for. |
| `PS3-I4` | `False` | A single non-circular PS3 instantiation ledger combining I1-I3. |

## Circularity Diagnostic

The current acceleration-rate algebra is

`delta_V - h (A_G \otimes I) delta_A = rho_V`,

hence

`delta_A = h^{-1} (A_G^{-1} \otimes I) (delta_V - rho_V)`.

This gives an `O(h^6)` unweighted acceleration rate only after using
`delta_V`, a component of the `P_state` perturbation. It is therefore
not an independent PS3 input for proving `P_state` itself.

The finite `h delta A` weighted probe is recorded, but it is not a
uniform compact-tube, non-circular PS3 input.

The h-acceleration obstruction audit records that the residual-only
finite nullity is `12`-`12`; adding the `h delta A` rows is what makes
the diagnostic weighted operator full column rank. This diagnostic is
not a theorem-level PS3 input.

## Acceptance Boundary

- This audit does not close actual PS3.
- `P_state` remains open.
- Zero P_state-induced Taylor bounds are certified.
- Primitive/Taylor PC2 lane remains open.
