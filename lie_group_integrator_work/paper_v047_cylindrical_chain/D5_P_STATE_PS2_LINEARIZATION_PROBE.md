# D5 P_state PS2 Linearization Probe

Status: **finite weighted linearization probe recorded; PS2 remains open**.

This diagnostic evaluates the accepted v047 residual Jacobian at solved
one-step Gauss stages. It forms the finite weighted operator
`(delta S, delta A) -> (D N_h^nd[delta S, delta A], h delta A)`
using the 96 non-dynamic rows and the state/acceleration columns. It
does not prove a uniform compact-tube inverse or inf-sup constant.

## Summary

- Case: `cylindrical_smooth`.
- Step sizes: `0.04, 0.02, 0.01`.
- State dimension: `72`.
- Acceleration dimension: `36`.
- Non-dynamic row dimension: `96`.
- Weighted operator shape: `132 x 108`.
- Full column rank in all finite probes: `True`.
- Rank range: `108..108`.
- Minimum singular value across probes: `9.999780e-03`.
- Maximum finite state projection constant: `2.019470e+00`.
- Maximum solved-stage residual norm: `1.221325e-14`.
- PS2 inverse or inf-sup closed: `False`.
- Primitive/Taylor PC2 route closed: `False`.

## Probe Rows

| h | rank | min singular | condition | state-projection constant | stage residual |
|---:|---:|---:|---:|---:|---:|
| `0.04000` | `108/108` | `3.998587e-02` | `3.627290e+02` | `2.019470e+00` | `1.029283e-14` |
| `0.02000` | `108/108` | `1.999824e-02` | `7.234843e+02` | `2.007889e+00` | `9.238507e-15` |
| `0.01000` | `108/108` | `9.999780e-03` | `1.446249e+03` | `2.005593e+00` | `1.221325e-14` |

## Acceptance Boundary

- The probe uses the implemented v047 Jacobian and the accepted row/column layout.
- The finite weighted operator is full column rank on the recorded probes.
- This is not a uniform compact-tube inverse or inf-sup proof.
- P_state, PS2, PC2, and the unconditional D5 theorem remain open.
