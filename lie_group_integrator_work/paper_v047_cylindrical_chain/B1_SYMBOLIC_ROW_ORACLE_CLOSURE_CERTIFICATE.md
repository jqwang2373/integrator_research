# B1 Symbolic Row-Oracle Closure Certificate

Status: **independent residual-row symbolic oracle closed; AD-expanded closure recorded in companion certificate**.

- Independent symbolic row-by-row oracle closed: `True`.
- Closed symbolic rows: `36/36`.
- Source/template symbolic identity rows: `36/36`.
- Runtime row binding checked rows: `36/36`.
- AD-expanded runtime formula binding checked rows: `36/36`.
- AD-expanded symbolic oracle closure by this certificate: `False`.
- Companion AD-expanded closure certificate closes the global B1 derivative-cell item: `True`.
- Dynamic symbolic oracle complete: `False`.
- O(h^7) symbolic-certificate proof closed by this certificate: `False`.
- Newton-Euler symbolic defect certificate complete: `False`.
- Certified O(h^7) rows in symbolic defect certificate: `0`.
- Remaining item inside this certificate only: `AD_expanded_symbolic_oracle_closure`.

## Boundary

This certificate closes only the B1 residual-row identity item: `independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows`.
It does not itself close the AD-expanded derivative symbolic oracle; that global B1 derivative-cell item is recorded by the companion AD-expanded closure certificate. This certificate still does not complete the Newton-Euler symbolic defect certificate or prove an O(h^7) dynamic-defect bound through the symbolic-certificate route.

## Row Closures

| row | stage | body | component | block | symbolic identity | runtime binding | closed |
|---:|---:|---:|---|---|---:|---:|---:|
| `24` | `0` | `0` | `x` | `translational_newton_balance` | `True` | `True` | `True` |
| `25` | `0` | `0` | `y` | `translational_newton_balance` | `True` | `True` | `True` |
| `26` | `0` | `0` | `z` | `translational_newton_balance` | `True` | `True` | `True` |
| `27` | `0` | `0` | `x` | `rotational_euler_balance` | `True` | `True` | `True` |
| `28` | `0` | `0` | `y` | `rotational_euler_balance` | `True` | `True` | `True` |
| `29` | `0` | `0` | `z` | `rotational_euler_balance` | `True` | `True` | `True` |
| `30` | `0` | `1` | `x` | `translational_newton_balance` | `True` | `True` | `True` |
| `31` | `0` | `1` | `y` | `translational_newton_balance` | `True` | `True` | `True` |
| `32` | `0` | `1` | `z` | `translational_newton_balance` | `True` | `True` | `True` |
| `33` | `0` | `1` | `x` | `rotational_euler_balance` | `True` | `True` | `True` |
| `34` | `0` | `1` | `y` | `rotational_euler_balance` | `True` | `True` | `True` |
| `35` | `0` | `1` | `z` | `rotational_euler_balance` | `True` | `True` | `True` |
| `68` | `1` | `0` | `x` | `translational_newton_balance` | `True` | `True` | `True` |
| `69` | `1` | `0` | `y` | `translational_newton_balance` | `True` | `True` | `True` |
| `70` | `1` | `0` | `z` | `translational_newton_balance` | `True` | `True` | `True` |
| `71` | `1` | `0` | `x` | `rotational_euler_balance` | `True` | `True` | `True` |
| `72` | `1` | `0` | `y` | `rotational_euler_balance` | `True` | `True` | `True` |
| `73` | `1` | `0` | `z` | `rotational_euler_balance` | `True` | `True` | `True` |
| `74` | `1` | `1` | `x` | `translational_newton_balance` | `True` | `True` | `True` |
| `75` | `1` | `1` | `y` | `translational_newton_balance` | `True` | `True` | `True` |
| `76` | `1` | `1` | `z` | `translational_newton_balance` | `True` | `True` | `True` |
| `77` | `1` | `1` | `x` | `rotational_euler_balance` | `True` | `True` | `True` |
| `78` | `1` | `1` | `y` | `rotational_euler_balance` | `True` | `True` | `True` |
| `79` | `1` | `1` | `z` | `rotational_euler_balance` | `True` | `True` | `True` |
| `112` | `2` | `0` | `x` | `translational_newton_balance` | `True` | `True` | `True` |
| `113` | `2` | `0` | `y` | `translational_newton_balance` | `True` | `True` | `True` |
| `114` | `2` | `0` | `z` | `translational_newton_balance` | `True` | `True` | `True` |
| `115` | `2` | `0` | `x` | `rotational_euler_balance` | `True` | `True` | `True` |
| `116` | `2` | `0` | `y` | `rotational_euler_balance` | `True` | `True` | `True` |
| `117` | `2` | `0` | `z` | `rotational_euler_balance` | `True` | `True` | `True` |
| `118` | `2` | `1` | `x` | `translational_newton_balance` | `True` | `True` | `True` |
| `119` | `2` | `1` | `y` | `translational_newton_balance` | `True` | `True` | `True` |
| `120` | `2` | `1` | `z` | `translational_newton_balance` | `True` | `True` | `True` |
| `121` | `2` | `1` | `x` | `rotational_euler_balance` | `True` | `True` | `True` |
| `122` | `2` | `1` | `y` | `rotational_euler_balance` | `True` | `True` | `True` |
| `123` | `2` | `1` | `z` | `rotational_euler_balance` | `True` | `True` | `True` |

## Source Evidence

- `NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json`: symbolic expansions, template instantiations, template algebraic equivalence, row-expanded virtual work identity, balance identity, smooth-force lift, and row-ordering/scaling evidence for all 36 rows.
- `NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json`: AD-expanded runtime formula binding evidence for 36 rows with 132 columns per row; this remains finite runtime binding evidence and not symbolic closure.

## Validation

Run `validate_b1_symbolic_row_oracle_closure_certificate.py`.
