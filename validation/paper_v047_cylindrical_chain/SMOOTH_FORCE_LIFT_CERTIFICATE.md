# Smooth Force Lift Certificate

Status: **D4 CLOSED - smooth force/friction lift is C7 on the accepted compact proof tube; dynamic defect remains open**.

- Source structure checked: `True`.
- Smooth-force consistency closed: `True`.
- Global C7 tube derivative bound proved: `True`.
- Stage residual O(h^7) defect proved: `False`.
- Stage residual false scope: `not proved by this D4 smooth-force certificate alone; this artifact supplies only the compact-tube C7 force/friction lift input`.
- Direct PC2 route source: `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json`.
- Submission ready: `False`.

## Checked Structure

| group | checked |
|---|---:|
| Brown-McPhee formula | `True` |
| normal-load regularization | `True` |
| fixed smooth-branch parameters | `True` |
| stage-local FullVA lift | `True` |
| friction smoothness sweep present | `True` |
| compact smooth proof-tube C7 audit | `True` |

## Compact Tube C7 Audit

- Derivative order: `7`.
- Accepted smooth stribeck velocity: `0.5`.
- Normal-load square-root lower bound: `1e-24`.
- Brown-McPhee rational denominator lower bound: `0.5625`.
- Scope: accepted cylindrical_smooth branch only; assumes the already accepted smooth FullVA stage lift stays in a compact proof tube; excludes the sharp/small-stribeck diagnostic branch and does not prove dynamic-row O(h^7) defect.

## Sweep Summary

- Smooth branch stribeck velocity: `0.5`.
- Sharp branch stribeck velocity: `0.05`.
- Smooth branch position/velocity order: `7.160828003417382` / `7.06618253965185`.
- Sharp branch position/velocity order: `1.8935250288226582` / `2.683371636159996`.

## Boundary

- This certificate closes only the D4 smooth force/friction lift sub-obligation on the accepted smooth branch.
- It relies on the already accepted compact smooth FullVA proof tube and excludes the sharp/small-stribeck diagnostic branch.
- It does not close the Newton-Euler dynamic O(h^7) defect certificate.

Validator: `validate_smooth_force_lift_certificate.py`.
