# Newton-Euler AD-Expanded Row Oracle Audit

Status: **AD-expanded runtime formula binding complete; symbolic oracle open**.

- AD-expanded row oracle closed: `True`.
- AD-expanded rows: `36/36`.
- AD columns per row: `132`.
- Formula-family-major offset: `72`.
- Formula-row AD Jacobian probes: `3`.
- Formula-row AD Jacobian max mismatch: `3.330669e-16`.
- AD-expanded symbolic oracle closure: `False`.
- Independent symbolic row-by-row oracle closed: `False`.
- Dynamic symbolic oracle complete: `False`.
- Stage residual O(h^7) implementation defect proved: `False`.

## Row Coverage

| accepted row | formula-major row | stage | body | component | block | columns | probes | binding |
|---:|---:|---:|---:|---|---|---:|---:|---:|
| `24` | `72` | `0` | `0` | `x` | `translational_newton_balance` | `132` | `3` | `True` |
| `25` | `73` | `0` | `0` | `y` | `translational_newton_balance` | `132` | `3` | `True` |
| `26` | `74` | `0` | `0` | `z` | `translational_newton_balance` | `132` | `3` | `True` |
| `27` | `75` | `0` | `0` | `x` | `rotational_euler_balance` | `132` | `3` | `True` |
| `28` | `76` | `0` | `0` | `y` | `rotational_euler_balance` | `132` | `3` | `True` |
| `29` | `77` | `0` | `0` | `z` | `rotational_euler_balance` | `132` | `3` | `True` |
| `30` | `78` | `0` | `1` | `x` | `translational_newton_balance` | `132` | `3` | `True` |
| `31` | `79` | `0` | `1` | `y` | `translational_newton_balance` | `132` | `3` | `True` |
| `32` | `80` | `0` | `1` | `z` | `translational_newton_balance` | `132` | `3` | `True` |
| `33` | `81` | `0` | `1` | `x` | `rotational_euler_balance` | `132` | `3` | `True` |
| `34` | `82` | `0` | `1` | `y` | `rotational_euler_balance` | `132` | `3` | `True` |
| `35` | `83` | `0` | `1` | `z` | `rotational_euler_balance` | `132` | `3` | `True` |
| `68` | `84` | `1` | `0` | `x` | `translational_newton_balance` | `132` | `3` | `True` |
| `69` | `85` | `1` | `0` | `y` | `translational_newton_balance` | `132` | `3` | `True` |
| `70` | `86` | `1` | `0` | `z` | `translational_newton_balance` | `132` | `3` | `True` |
| `71` | `87` | `1` | `0` | `x` | `rotational_euler_balance` | `132` | `3` | `True` |
| `72` | `88` | `1` | `0` | `y` | `rotational_euler_balance` | `132` | `3` | `True` |
| `73` | `89` | `1` | `0` | `z` | `rotational_euler_balance` | `132` | `3` | `True` |
| `74` | `90` | `1` | `1` | `x` | `translational_newton_balance` | `132` | `3` | `True` |
| `75` | `91` | `1` | `1` | `y` | `translational_newton_balance` | `132` | `3` | `True` |
| `76` | `92` | `1` | `1` | `z` | `translational_newton_balance` | `132` | `3` | `True` |
| `77` | `93` | `1` | `1` | `x` | `rotational_euler_balance` | `132` | `3` | `True` |
| `78` | `94` | `1` | `1` | `y` | `rotational_euler_balance` | `132` | `3` | `True` |
| `79` | `95` | `1` | `1` | `z` | `rotational_euler_balance` | `132` | `3` | `True` |
| `112` | `96` | `2` | `0` | `x` | `translational_newton_balance` | `132` | `3` | `True` |
| `113` | `97` | `2` | `0` | `y` | `translational_newton_balance` | `132` | `3` | `True` |
| `114` | `98` | `2` | `0` | `z` | `translational_newton_balance` | `132` | `3` | `True` |
| `115` | `99` | `2` | `0` | `x` | `rotational_euler_balance` | `132` | `3` | `True` |
| `116` | `100` | `2` | `0` | `y` | `rotational_euler_balance` | `132` | `3` | `True` |
| `117` | `101` | `2` | `0` | `z` | `rotational_euler_balance` | `132` | `3` | `True` |
| `118` | `102` | `2` | `1` | `x` | `translational_newton_balance` | `132` | `3` | `True` |
| `119` | `103` | `2` | `1` | `y` | `translational_newton_balance` | `132` | `3` | `True` |
| `120` | `104` | `2` | `1` | `z` | `translational_newton_balance` | `132` | `3` | `True` |
| `121` | `105` | `2` | `1` | `x` | `rotational_euler_balance` | `132` | `3` | `True` |
| `122` | `106` | `2` | `1` | `y` | `rotational_euler_balance` | `132` | `3` | `True` |
| `123` | `107` | `2` | `1` | `z` | `rotational_euler_balance` | `132` | `3` | `True` |

## Boundary

This audit closes row-level AD-expanded runtime/formula binding coverage only.
It does not prove a symbolic identity for the expanded rows, and it does not
prove the Newton-Euler stage residual is O(h^7).

Validator: `validate_newton_euler_ad_expanded_row_oracle_audit.py`.
