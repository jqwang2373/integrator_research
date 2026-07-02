# CMAME Scalability Boundary Audit

Status: **reference implementation scalability boundary recorded; B7 remains open**.

- Read-only audit: `True`.
- Invoked `run_v047.py`: `False`.
- B7 closed: `False`.
- Performance superiority claim allowed: `False`.
- Production scalability claim allowed: `False`.
- Reference residual dimension: `132`.
- Sparse pattern nonzeros: `2637`.
- Column/row colors: `90/60`.
- Row runtime over dense `jacfwd`: `1.203` to `1.224`.
- Row-runtime reduction needed to match dense: `16.9%` to `18.3%`.

## Sparse Timing Boundary

| case | dense sec | row sec | row/dense | row colors | dense faster | block assembly needed |
|---|---:|---:|---:|---:|---|---|
| cylindrical_smooth | 1.070e-01 | 1.309e-01 | 1.224 | 60 | `True` | `True` |
| cylindrical_sharp | 1.098e-01 | 1.322e-01 | 1.203 | 60 | `True` | `True` |

## Work-Precision Boundary

- Strict common-reference work/precision figure present: `True`.
- Coarse baseline work/precision figure present: `True`.
- Common-reference order/error wins: `40/40`.
- Source-policy rows closed: `0/40`.
- External source-policy superiority remains disallowed.

## Missing Scalability Campaign

- N-body chain sweep present: `False`.
- Requested body counts: `N=2,4,8,16,32`.
- Completed body counts: `[]`.
- Wall-clock, Newton-iteration, Jacobian-assembly, linear-solve, condition, and memory scaling versus body count are not yet present.

## Required To Close

- N-body chain benchmark for N=2,4,8,16,32.
- dense AD versus sparse/block Jacobian timing.
- wall-clock, Newton-iteration, Jacobian-assembly, and linear-solve breakdowns.
- condition-number or rank diagnostics versus body count.
- memory scaling versus body count.
- complete source-policy work-precision curves for external suites.
