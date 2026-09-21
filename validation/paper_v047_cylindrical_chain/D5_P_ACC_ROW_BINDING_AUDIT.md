# D5 P_acc Row-Binding Audit

Status: **P_acc row binding closed; lift remains open**.

This read-only audit closes only PA4 for `P_acc`: the 36
acceleration-lift Taylor terms are bound to the implemented D6 row
ordering and runtime residual source components. It does not prove an
`O(h^7)` acceleration lift rate.

## Summary

- Closed P_acc subproofs after binding: `2/4`.
- Open P_acc subproofs after binding: `2`.
- Acceleration rows bound to ordering: `36/36`.
- Rows with closed binding: `36/36`.
- Translational/angular acceleration rows: `18/18`.
- P_acc primitive closed: `False`.
- Acceleration lift rate proved: `False`.
- Taylor bounds proved: `0/36`.
- Conditional row-level P_acc corollary present main/flat: `True/True`.
- Primitive/Taylor PC2 route closed: `False`.

## Row Binding

The accepted acceleration-lift rows occupy global rows `24--35`,
`68--79`, and `112--123`. For each row, the D5 Taylor-term budget
stage/body/component entry matches the D6 runtime row ordering and
runtime source component.

## Acceptance Boundary

- PA1 map definition is closed.
- PA4 row-ordering/Taylor-term binding is closed.
- PA2 velocity-collocation-to-acceleration lift proof remains open.
- PA3 independence is not closed by this row-binding audit; the later independence audit closes PA3 separately.
- `P_acc` remains open.
- Primitive/Taylor PC2 lane remains open.
