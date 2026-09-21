# D5 Dynamic Direct-Substitution Certificate

Status: **direct-substitution certificate closed**.

This certificate records the non-circular D5 route in which the accepted
residual is evaluated directly at `Z_G`, the smooth FullVA lift of the
reduced Gauss stage. It is a proof artifact, not a numerical probe.

## Summary

- Dynamic rows checked: `36/36`.
- Translational/rotational rows: `18/18`.
- Dynamic zero-residual rows by direct substitution: `36/36`.
- Existing certified non-dynamic rows: `96/96`.
- Full stage rows covered when assembled by the full-residual bridge: `132/132`.
- Direct-route residual-remainder status: the residual remainder is zero after direct substitution, so the row bound is stronger than `O(h^7)`.
- Primitive Taylor lane status: this does not certify the primitive 162-subterm Taylor lane.
- Forbidden shortcut count: `0`.
- Direct route certificate closed: `True`.

## Direct Proof Logic

1. Construct `Z_G` from the smooth FullVA lift of the reduced Gauss stage.
2. The existing 96-row certificate gives an `O(h^7)` non-dynamic residual bound on the same lift.
3. For each Newton-Euler row, D1/D2 reduce the implemented row to the accepted balance identity.
4. D3 supplies the multiplier-wrench identity, D4 supplies the smooth force/friction branch, and D6 supplies row ordering/scaling/AD binding.
5. The smooth FullVA lift satisfies the pointwise Newton-Euler balance at the lifted stage, so each dynamic row evaluates to `0`, hence to `O(h^7)`.

## Non-Circularity

- No `P_state` actual PS3 estimate is used as an input.
- No `P_acc` or `P_lambda` lift-rate primitive is used as an input.
- No finite probe is promoted to proof.
- No residual-to-error theorem is used to prove the row defect.
- The h-acceleration obstruction is bypassed by using the full 132-row residual route.

## Active-Route Boundary

This artifact proves the row-local direct-substitution route consumed by the
active PC2 closure route, namely the active direct PC2 residual bridge.
It does not certify the optional
primitive/Taylor route or any source-policy package claim.

## Row Proofs

| row | stage | body | comp. | block | identity | residual |
|---:|---:|---:|---|---|---|---|
| `24` | `0` | `0` | `x` | `translational_newton_balance` | `D1` | `0` |
| `25` | `0` | `0` | `y` | `translational_newton_balance` | `D1` | `0` |
| `26` | `0` | `0` | `z` | `translational_newton_balance` | `D1` | `0` |
| `27` | `0` | `0` | `x` | `rotational_euler_balance` | `D2` | `0` |
| `28` | `0` | `0` | `y` | `rotational_euler_balance` | `D2` | `0` |
| `29` | `0` | `0` | `z` | `rotational_euler_balance` | `D2` | `0` |
| `30` | `0` | `1` | `x` | `translational_newton_balance` | `D1` | `0` |
| `31` | `0` | `1` | `y` | `translational_newton_balance` | `D1` | `0` |
| `32` | `0` | `1` | `z` | `translational_newton_balance` | `D1` | `0` |
| `33` | `0` | `1` | `x` | `rotational_euler_balance` | `D2` | `0` |
| `34` | `0` | `1` | `y` | `rotational_euler_balance` | `D2` | `0` |
| `35` | `0` | `1` | `z` | `rotational_euler_balance` | `D2` | `0` |
| `68` | `1` | `0` | `x` | `translational_newton_balance` | `D1` | `0` |
| `69` | `1` | `0` | `y` | `translational_newton_balance` | `D1` | `0` |
| `70` | `1` | `0` | `z` | `translational_newton_balance` | `D1` | `0` |
| `71` | `1` | `0` | `x` | `rotational_euler_balance` | `D2` | `0` |
| `72` | `1` | `0` | `y` | `rotational_euler_balance` | `D2` | `0` |
| `73` | `1` | `0` | `z` | `rotational_euler_balance` | `D2` | `0` |
| `74` | `1` | `1` | `x` | `translational_newton_balance` | `D1` | `0` |
| `75` | `1` | `1` | `y` | `translational_newton_balance` | `D1` | `0` |
| `76` | `1` | `1` | `z` | `translational_newton_balance` | `D1` | `0` |
| `77` | `1` | `1` | `x` | `rotational_euler_balance` | `D2` | `0` |
| `78` | `1` | `1` | `y` | `rotational_euler_balance` | `D2` | `0` |
| `79` | `1` | `1` | `z` | `rotational_euler_balance` | `D2` | `0` |
| `112` | `2` | `0` | `x` | `translational_newton_balance` | `D1` | `0` |
| `113` | `2` | `0` | `y` | `translational_newton_balance` | `D1` | `0` |
| `114` | `2` | `0` | `z` | `translational_newton_balance` | `D1` | `0` |
| `115` | `2` | `0` | `x` | `rotational_euler_balance` | `D2` | `0` |
| `116` | `2` | `0` | `y` | `rotational_euler_balance` | `D2` | `0` |
| `117` | `2` | `0` | `z` | `rotational_euler_balance` | `D2` | `0` |
| `118` | `2` | `1` | `x` | `translational_newton_balance` | `D1` | `0` |
| `119` | `2` | `1` | `y` | `translational_newton_balance` | `D1` | `0` |
| `120` | `2` | `1` | `z` | `translational_newton_balance` | `D1` | `0` |
| `121` | `2` | `1` | `x` | `rotational_euler_balance` | `D2` | `0` |
| `122` | `2` | `1` | `y` | `rotational_euler_balance` | `D2` | `0` |
| `123` | `2` | `1` | `z` | `rotational_euler_balance` | `D2` | `0` |
