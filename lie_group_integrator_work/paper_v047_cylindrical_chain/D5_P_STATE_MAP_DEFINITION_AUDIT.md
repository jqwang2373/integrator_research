# D5 P_state Map Definition Audit

Status: **P_state map definition closed; lift remains open**.

This read-only audit closes only PS1 for `P_state`: the non-dynamic
stage map is defined in the accepted Lie chart and bound to the 96
certified non-dynamic row families. It does not prove a local inverse,
an inf-sup bound, or any `O(h^7)` state lift rate.

## Summary

- Closed P_state subproofs: `1/4`.
- Open P_state subproofs in this map audit: `2`.
- Aggregate P_state subproofs closed after PS4: `2/4`.
- PS4 anti-circularity closed elsewhere: `True`.
- Non-dynamic map rows: `96/96`.
- Term rows using P_state: `126/162`.
- P_state primitive closed: `False`.
- State lift rate proved: `False`.
- Primitive/Taylor PC2 route closed: `False`.

## Map Interface

`N_h^nd(S,A)` collects the accepted non-dynamic residual rows with
`S=(r_i, eta_i, v_i, omega_i)` and auxiliary acceleration block
`A=(a_i, alpha_i)`. The multiplier block is excluded from this
map-definition subproof.

| row family | rows | in 96-row certificate |
|---|---:|---:|
| `translational_position_weak_defect` | `18` | `True` |
| `rotational_lie_position_weak_defect` | `18` | `True` |
| `translational_velocity_weak_defect` | `18` | `True` |
| `angular_velocity_weak_defect` | `18` | `True` |
| `lower_pair_index3_weak_constraints` | `24` | `True` |

## Acceptance Boundary

- PS1 map definition is closed.
- PS2 local inverse or inf-sup proof remains open.
- PS3 conversion to `O(h^7)` state lift rates remains open.
- PS4 anti-circularity is closed separately by `D5_P_STATE_ANTICIRCULARITY_AUDIT`.
- `P_state` remains open.
- Primitive/Taylor PC2 lane remains open.
