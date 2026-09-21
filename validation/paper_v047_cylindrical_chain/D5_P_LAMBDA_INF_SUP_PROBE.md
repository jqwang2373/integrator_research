# D5 P_lambda Inf-Sup Probe

Status: **finite multiplier-column inf-sup probe recorded; finite probe itself does not close PL2**.

This diagnostic evaluates the accepted dynamic-row Jacobian subblock
`D_lambda R_dyn` on solved one-step Gauss6/FullVA stages. It records
finite full-column-rank evidence for the multiplier-column interface,
but it is not a uniform compact-tube inf-sup proof.

## Summary

- Probe rows: `3`.
- Dynamic row dimension: `36`.
- Lambda column dimension: `24`.
- Operator shape: `[36, 24]`.
- Full column rank in all finite probes: `True`.
- Minimum singular value across probes: `6.142804e-01`.
- Maximum condition number across probes: `2.770741e+00`.
- Maximum finite multiplier recovery constant: `1.627921e+00`.
- PL2 uniform inf-sup bound proved: `False`.
- Multiplier lift rate proved: `False`.
- Primitive/Taylor PC2 route closed: `False`.

## Probe Rows

| h | rank | lambda columns | min singular value | condition | stage residual |
|---:|---:|---:|---:|---:|---:|
| `0.04` | `24` | `24` | `6.143764e-01` | `2.770629e+00` | `1.029283e-14` |
| `0.02` | `24` | `24` | `6.143122e-01` | `2.770741e+00` | `9.238507e-15` |
| `0.01` | `24` | `24` | `6.142804e-01` | `2.769346e+00` | `1.221325e-14` |

## Acceptance Boundary

- This is a finite solved-stage rank diagnostic.
- It supports the plausibility of the PL2 multiplier-column estimate.
- It does not prove a uniform compact-tube inf-sup constant.
- It does not prove a multiplier lift rate or certify Taylor bounds.
- The finite probe itself does not close PL2; P_lambda, PC2, and the unconditional D5 theorem remain open.
