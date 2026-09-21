# D5 P_acc PA2 Weighted-Inverse Audit

Status: **PA2 weighted-inverse diagnostic recorded; unweighted lift remains open**.

This read-only audit evaluates the same finite weighted PS2 operator
used for the state-lift target and records projection constants for
`delta S`, `delta A`, and `h delta A`. It is a diagnostic, not a
uniform compact-tube inverse proof.

## Summary

- Probe count: `3`.
- Weighted operator full column rank in all probes: `True`.
- Max unweighted acceleration projection constant: `1.000000e+02`.
- Max weighted h-acceleration projection constant: `1.000000e+00`.
- Weighted h-acceleration control recorded: `True`.
- Unweighted acceleration uniform control proved: `False`.
- PA2 closed: `False`.
- P_acc primitive closed: `False`.
- Primitive/Taylor PC2 route closed: `False`.

## Acceptance Boundary

- The finite weighted operator supports bounded finite control of `h delta A`.
- The audit does not prove a uniform unweighted acceleration lift.
- PA2 remains open.
- `P_acc` remains open.
- Primitive/Taylor PC2 lane remains open.
