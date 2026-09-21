# Newton-Euler Row Ordering, Scaling, and AD Audit

Status: **D6 CLOSED - row ordering, residual scaling, and AD binding are checked; dynamic defect remains open**.

- Symbolic runtime row-equivalence sub-obligation closed: `True`.
- Row-ordering/scaling/AD closed: `True`.
- Dynamic symbolic oracle complete: `False`.
- Stage residual O(h^7) implementation defect proved: `False`.
- Local D6 audit proof gap closed: `False`.
- Proof gap closed scope: `local_d6_row_ordering_scaling_ad_audit_only; this audit closes implementation layout/AD binding but not the D5 O(h^7) dynamic defect or the full direct D5/PC2 closure artifact`.
- Submission ready: `False`.

## Row Layout

- Stage size: `44`.
- Dynamic offset/width: `24/12`.
- Per-stage dynamic order: body0 translational, body0 rotational, body1 translational, body1 rotational.
- Global row formula: `global_row = 44*stage + 24 + local_dynamic_offset`.

## Checked Groups

| group | checked |
|---|---:|
| source row order and unweighted residual scaling | `True` |
| target-row layout equivalence | `True` |
| accepted AD binding | `True` |

## Boundary

- This closes only D6: implemented row ordering, unweighted residual scaling, and accepted AD binding.
- It does not close the D1/D2 balance identities.
- It does not prove the D5 O(h^7) dynamic-row defect.

Validator: `validate_newton_euler_row_ordering_scaling_ad_audit.py`.
