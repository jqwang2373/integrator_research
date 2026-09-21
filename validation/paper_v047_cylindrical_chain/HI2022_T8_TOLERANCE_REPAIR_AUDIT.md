# HI2022 T=8 Tolerance-Repair Audit

Status: **tolerance repair recorded; source-policy closure still open**.

- Original T=8 coarse rows ok: `18/24`.
- Original complete form/model groups: `4/8`.
- Repair rows ok: `7/12`.
- Repair complete form/model groups: `0/4`.
- Second repair rows ok: `13/18`.
- Second repair complete form/model groups: `2/6`.
- Combined best rows ok: `19/24`.
- Combined best complete form/model groups: `4/8`.
- Recovered rows: `1`.
- Remaining incomplete groups: `4`.
- Repair tolerance base: `1e-07`.
- Additional repair tolerance base: `1e-06`.
- Contains source-policy 1e-4 rows: `False`.
- Source-policy reproduction closed: `False`.
- Full T=8 policy completed: `False`.
- External superiority claim allowed: `False`.

## Recovered Rows

| form | model | h | status | max iterations |
|---|---|---:|---|---:|
| `rA_half` | `double_pendulum` | `0.025` | `ok` | `54.0` |

## Remaining Incomplete Groups

| group | ok rows | failed rows | failure families | failed h/status |
|---|---:|---:|---|---|
| `rA:slider_crank` | `2/3` | `1` | `{'nan_or_singular_matrix': 1, 'ok': 2}` | `h=0.1: nan_or_singular_matrix (failed:ValueError:array must not contain infs or NaNs)` |
| `rA_half:double_pendulum` | `1/3` | `2` | `{'newton_not_converging': 2, 'ok': 1}` | `h=0.05: newton_not_converging (failed:RuntimeError:Newton-Raphson not converging at t: 5.850, k: 100); h=0.1: newton_not_converging (failed:RuntimeError:Newton-Raphson not converging at t: 5.000, k: 100)` |
| `rA_half:four_link` | `2/3` | `1` | `{'newton_not_converging': 1, 'ok': 2}` | `h=0.1: newton_not_converging (failed:RuntimeError:Newton-Raphson not converging at t: 0.700, k: 100)` |
| `rA_half:slider_crank` | `2/3` | `1` | `{'nan_or_singular_matrix': 1, 'ok': 2}` | `h=0.1: nan_or_singular_matrix (failed:ValueError:array must not contain infs or NaNs)` |

## Full Public-Grid Contract

- Full public-grid required rows: `72`.
- Full public-grid required form/model groups: `8`.
- Public step sizes: `0.0001, 0.0002, 0.0004, 0.001, 0.002, 0.004, 0.01, 0.02, 0.04`.
- Public reference h: `0.001`.
- Public tolerance base: `1e-10`.
- Current repair step sizes: `0.1, 0.05, 0.025`.
- Current repair reference h: `0.0125`.
- Current repair matches public step grid: `False`.
- Current repair matches public reference h: `False`.
- Post-B4 decision: `demote_from_b4_b7_source_policy_figures`.
- Targeted repair required before promotion: `True`.
- Do not rerun guarded driver blindly: `True`.
- Rows promoted: `0`.

## Targeted Repair Acceptance Contract

- Coarse-trio repair must first complete `rA_half:double_pendulum` at h=`0.1`, `0.05`, and `0.025` with finite error and work metrics.
- Coarse-trio success remains diagnostic and is not full public-grid source-policy closure.
- Full promotion requires all `72` public-grid rows with T=`8.0`, reference h=`0.001`, tolerance base=`1e-10`, output norm, runtime, and Newton diagnostics bound.

## Failure Families

- Original: `{'ok': 18, 'newton_not_converging': 4, 'nan_or_singular_matrix': 2}`.
- Repair: `{'newton_not_converging': 3, 'ok': 7, 'nan_or_singular_matrix': 2}`.
- Second repair: `{'ok': 13, 'newton_not_converging': 3, 'nan_or_singular_matrix': 2}`.

Interpretation: relaxing the tolerance records a useful negative result. The first repair recovers one row, and the second non-heavy 1e-6 sweep does not increase the combined-best closure beyond 19/24 rows and 4/8 groups. The source-policy claim remains open.

Validator: `validate_hi2022_t8_tolerance_repair_audit.py`.
