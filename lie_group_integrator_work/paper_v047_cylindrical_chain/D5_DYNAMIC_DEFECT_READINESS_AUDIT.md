# D5 Dynamic-Defect Readiness Audit

Status: **D5 direct-substitution closure recorded; primitive/Taylor route remains open**.

This read-only audit records the row-local direct-substitution closure
for the 36 Newton-Euler dynamic rows. It also preserves the separate
primitive/Taylor route as open.

## Summary

- Rows checked: `36/36`.
- Translational/rotational rows: `18/18`.
- Runtime-traceability-ready rows: `36/36`.
- Rows requiring defect power at least seven: `36/36`.
- Open lifted-stage dynamic terms: `0/36`.
- Direct-substitution closed rows: `36/36`.
- Direct-substitution dynamic zero rows: `36/36`.
- Primitive/Taylor closed rows: `0/36`.
- Direct-route certified rows: `36/36`.
- Finite-probe-sufficient rows: `0/36`.
- Residual-to-error-promotion rows: `0/36`.
- Manuscript D5 Taylor target table present in main/flat TeX: `True/True`.
- Stage residual O(h^7) implementation defect proved: `True`.
- Direct PC2 row-defect route closed: `True`.
- Proof gap closed scope: `direct_substitution_row_defect_pc2_only`.
- Primitive/Taylor route closed: `False`.
- Residual-to-error route closed: `False`.
- Multiplier/reaction output order claimed: `False`.
- Submission ready: `False`.

## Required D5 Statement

For each row, substitute the smooth FullVA Gauss lift `Z_G` into the
expanded Newton-Euler row. The D5 direct-substitution certificate records
zero residual row-by-row, hence an `O(h^7)` bound. Finite probes and
residual-to-error promotion do not satisfy this acceptance test.

## Row Coverage

| row | stage | body | block | component | closed inputs | open term | direct residual |
|---:|---:|---:|---|---|---:|---|---|
| `24` | `0` | `0` | translational_newton_balance | `x` | `5/5` | `` | `0` |
| `25` | `0` | `0` | translational_newton_balance | `y` | `5/5` | `` | `0` |
| `26` | `0` | `0` | translational_newton_balance | `z` | `5/5` | `` | `0` |
| `27` | `0` | `0` | rotational_euler_balance | `x` | `5/5` | `` | `0` |
| `28` | `0` | `0` | rotational_euler_balance | `y` | `5/5` | `` | `0` |
| `29` | `0` | `0` | rotational_euler_balance | `z` | `5/5` | `` | `0` |
| `30` | `0` | `1` | translational_newton_balance | `x` | `5/5` | `` | `0` |
| `31` | `0` | `1` | translational_newton_balance | `y` | `5/5` | `` | `0` |
| `32` | `0` | `1` | translational_newton_balance | `z` | `5/5` | `` | `0` |
| `33` | `0` | `1` | rotational_euler_balance | `x` | `5/5` | `` | `0` |
| `34` | `0` | `1` | rotational_euler_balance | `y` | `5/5` | `` | `0` |
| `35` | `0` | `1` | rotational_euler_balance | `z` | `5/5` | `` | `0` |
| `68` | `1` | `0` | translational_newton_balance | `x` | `5/5` | `` | `0` |
| `69` | `1` | `0` | translational_newton_balance | `y` | `5/5` | `` | `0` |
| `70` | `1` | `0` | translational_newton_balance | `z` | `5/5` | `` | `0` |
| `71` | `1` | `0` | rotational_euler_balance | `x` | `5/5` | `` | `0` |
| `72` | `1` | `0` | rotational_euler_balance | `y` | `5/5` | `` | `0` |
| `73` | `1` | `0` | rotational_euler_balance | `z` | `5/5` | `` | `0` |
| `74` | `1` | `1` | translational_newton_balance | `x` | `5/5` | `` | `0` |
| `75` | `1` | `1` | translational_newton_balance | `y` | `5/5` | `` | `0` |
| `76` | `1` | `1` | translational_newton_balance | `z` | `5/5` | `` | `0` |
| `77` | `1` | `1` | rotational_euler_balance | `x` | `5/5` | `` | `0` |
| `78` | `1` | `1` | rotational_euler_balance | `y` | `5/5` | `` | `0` |
| `79` | `1` | `1` | rotational_euler_balance | `z` | `5/5` | `` | `0` |
| `112` | `2` | `0` | translational_newton_balance | `x` | `5/5` | `` | `0` |
| `113` | `2` | `0` | translational_newton_balance | `y` | `5/5` | `` | `0` |
| `114` | `2` | `0` | translational_newton_balance | `z` | `5/5` | `` | `0` |
| `115` | `2` | `0` | rotational_euler_balance | `x` | `5/5` | `` | `0` |
| `116` | `2` | `0` | rotational_euler_balance | `y` | `5/5` | `` | `0` |
| `117` | `2` | `0` | rotational_euler_balance | `z` | `5/5` | `` | `0` |
| `118` | `2` | `1` | translational_newton_balance | `x` | `5/5` | `` | `0` |
| `119` | `2` | `1` | translational_newton_balance | `y` | `5/5` | `` | `0` |
| `120` | `2` | `1` | translational_newton_balance | `z` | `5/5` | `` | `0` |
| `121` | `2` | `1` | rotational_euler_balance | `x` | `5/5` | `` | `0` |
| `122` | `2` | `1` | rotational_euler_balance | `y` | `5/5` | `` | `0` |
| `123` | `2` | `1` | rotational_euler_balance | `z` | `5/5` | `` | `0` |

## Boundary

- Allowed now: row-local direct-substitution D5 closure and a precise primitive/Taylor non-closure boundary.
- Forbidden now: primitive/Taylor-route closure, finite-probe-only D5 closure, residual-to-error D5 closure, or submission-ready proof.
