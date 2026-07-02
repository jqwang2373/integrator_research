# Newton-Euler Balance Identity Audit

Status: **d1_d2_balance_identities_closed_d5_dynamic_defect_open**.

Scope note: D1/D2-only balance audit. The false D5 and stage-residual booleans mean not proved by this audit alone. Current theorem-level D5/direct-route status is determined by D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE and NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT; the optional symbolic/primitive certificate route remains separate.

- Row family: `newton_euler_weak_balance`.
- Rows checked: `36`.
- Balance identity closed rows: `36`.
- Translational D1 rows closed: `18/18`.
- Rotational D2 rows closed: `18/18`.
- Template algebraic equivalence rows: `36`.
- Runtime-template instantiation rows: `36`.
- Body-specific wrench-expansion rows: `36`.
- D3 multiplier-wrench consistency rows: `36`.
- D4 smooth force-lift consistency rows: `36`.
- D6 row-ordering/scaling/AD rows: `36`.
- D5 dynamic defect rate closed: `False`.
- Stage residual O(h^7) implementation defect proved: `False`.
- Submission ready: `False`.

## Boundary

The audit closes the source-level Newton-Euler balance identities by combining runtime-template instantiation, body-specific sign expansion, scalar symbolic template equality, D3 multiplier-wrench consistency, D4 smooth force lift, and D6 row-ordering/scaling/AD binding.  It does not substitute the lifted Gauss solution into the dynamic rows and therefore does not prove D5 by itself. The current direct D5 theorem status is supplied elsewhere by D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE and NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.

## Row Evidence

| row | stage | body | component | identity | closed | simplified difference |
|---:|---:|---:|---|---|---:|---|
| 24 | 0 | 0 | x | D1 | `True` | `0` |
| 25 | 0 | 0 | y | D1 | `True` | `0` |
| 26 | 0 | 0 | z | D1 | `True` | `0` |
| 27 | 0 | 0 | x | D2 | `True` | `0` |
| 28 | 0 | 0 | y | D2 | `True` | `0` |
| 29 | 0 | 0 | z | D2 | `True` | `0` |
| 30 | 0 | 1 | x | D1 | `True` | `0` |
| 31 | 0 | 1 | y | D1 | `True` | `0` |
| 32 | 0 | 1 | z | D1 | `True` | `0` |
| 33 | 0 | 1 | x | D2 | `True` | `0` |
| 34 | 0 | 1 | y | D2 | `True` | `0` |
| 35 | 0 | 1 | z | D2 | `True` | `0` |
| 68 | 1 | 0 | x | D1 | `True` | `0` |
| 69 | 1 | 0 | y | D1 | `True` | `0` |
| 70 | 1 | 0 | z | D1 | `True` | `0` |
| 71 | 1 | 0 | x | D2 | `True` | `0` |
| 72 | 1 | 0 | y | D2 | `True` | `0` |
| 73 | 1 | 0 | z | D2 | `True` | `0` |
| 74 | 1 | 1 | x | D1 | `True` | `0` |
| 75 | 1 | 1 | y | D1 | `True` | `0` |
| 76 | 1 | 1 | z | D1 | `True` | `0` |
| 77 | 1 | 1 | x | D2 | `True` | `0` |
| 78 | 1 | 1 | y | D2 | `True` | `0` |
| 79 | 1 | 1 | z | D2 | `True` | `0` |
| 112 | 2 | 0 | x | D1 | `True` | `0` |
| 113 | 2 | 0 | y | D1 | `True` | `0` |
| 114 | 2 | 0 | z | D1 | `True` | `0` |
| 115 | 2 | 0 | x | D2 | `True` | `0` |
| 116 | 2 | 0 | y | D2 | `True` | `0` |
| 117 | 2 | 0 | z | D2 | `True` | `0` |
| 118 | 2 | 1 | x | D1 | `True` | `0` |
| 119 | 2 | 1 | y | D1 | `True` | `0` |
| 120 | 2 | 1 | z | D1 | `True` | `0` |
| 121 | 2 | 1 | x | D2 | `True` | `0` |
| 122 | 2 | 1 | y | D2 | `True` | `0` |
| 123 | 2 | 1 | z | D2 | `True` | `0` |

## Non-Closure

This audit is not a dynamic-defect certificate.  The D5 proof must still substitute the lifted Gauss stage into the assembled dynamic rows and prove the residual is `O(h^7)`.
