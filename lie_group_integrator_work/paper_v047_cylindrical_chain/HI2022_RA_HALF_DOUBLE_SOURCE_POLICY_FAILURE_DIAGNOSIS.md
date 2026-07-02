# HI2022 rA_half Double Source-Policy Failure Diagnosis

Status: **diagnosis only; partial Newton-failure shard is not promoted**.

This artifact reads the completed isolated candidate rows and does not invoke any numerical runner.

- Candidate summary status: `partial_or_failed_full_T8_source_policy_candidate_not_promoted`.
- Form/model: `rA_half` / `double_pendulum`.
- T=8/source reference selected: `True` / `True`.
- Selected step sizes: `[0.02, 0.01, 0.005]`.
- Rows ok/failed/total: `1/2/3`.
- Selected step trio completed: `False`.
- Newton failure count: `2`.
- Failed h values: `[0.02, 0.01]`.
- Failure loci: `[{'h': 0.02, 'tolerance': 1e-10, 'failure_time': 2.24, 'failure_iteration_k': 100, 'message_parsed': True}, {'h': 0.01, 'tolerance': 1e-10, 'failure_time': 5.8, 'failure_iteration_k': 100, 'message_parsed': True}]`.
- Selected tolerance values: `[1e-10]`.
- Tolerance repair combined best rows/groups: `19/24` rows, `4/8` groups.
- Tolerance repair source-policy closed: `False`.
- Pair orders available: `False`.
- Promotion ready: `False`.
- Source-policy rows promoted by this diagnosis: `0`.
- B4/B7 can close from this diagnosis: `False`.

## Rows

| h | tolerance | status | failure t | failure k | pos final linf | vel final linf | acc final linf | avg iters | max iters | runtime sec |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `0.020` | `1.000e-10` | `failed:RuntimeError:Newton-Raphson not converging at t: 2.240, k: 100` | `2.240` | `100` | `nan` | `nan` | `nan` | `nan` | `nan` | `nan` |
| `0.010` | `1.000e-10` | `failed:RuntimeError:Newton-Raphson not converging at t: 5.800, k: 100` | `5.800` | `100` | `nan` | `nan` | `nan` | `nan` | `nan` | `nan` |
| `5.000e-03` | `1.000e-10` | `ok` | `nan` | `None` | `2.877` | `118.280` | `4.278e+03` | `10.453` | `22.000` | `2.685` |

## Decision

The isolated HI2022 rA_half double-pendulum T=8 selected-coarse-trio shard completed only the h=0.005 row; h=0.02 and h=0.01 failed with Newton-Raphson nonconvergence, leaving no pairwise order or publication work/precision curve.

These rows remain a root-cause diagnostic for B4/B7, not row-closure or external-superiority evidence.
