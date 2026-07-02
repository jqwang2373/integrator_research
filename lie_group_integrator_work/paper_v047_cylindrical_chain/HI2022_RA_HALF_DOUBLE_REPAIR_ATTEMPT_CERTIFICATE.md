# HI2022 rA_half Double Repair-Attempt Certificate

Status: **targeted repair attempted; not reproducible; not promoted**.

- Target: `rA_half:double_pendulum`.
- Source-policy rows promoted: `0`.
- External-superiority ready: `False`.
- B4/B7 can close from certificate: `False/False`.
- Initial selected-trio ok/failed rows: `1/2`.
- Combined repair target ok/failed rows: `1/2`.
- Combined best matrix ok rows/groups: `19/24` rows, `4/8` groups.
- Full public-grid rows required: `72`.
- Repair/public reference h: `0.0125/0.001`.
- Repair/public tolerance base: `1e-07/1e-10`.
- Full T=8 policy completed: `False`.
- Source-policy reproduction closed: `False`.

## Failed Target Rows

| h | best status | failure family | attempts |
|---:|---|---|---:|
| `0.05` | `failed:RuntimeError:Newton-Raphson not converging at t: 5.850, k: 100` | `newton_not_converging` | `3` |
| `0.1` | `failed:RuntimeError:Newton-Raphson not converging at t: 5.000, k: 100` | `newton_not_converging` | `3` |

## Repair Attempts

| tolerance base | target ok/failed | target complete | summary ok/rows | summary groups |
|---:|---:|---:|---:|---:|
| `1e-07` | `1/2` | `False` | `7/12` | `0/4` |
| `1e-06` | `1/2` | `False` | `13/18` | `2/6` |

The targeted repair recovers only the h=0.025 row for rA_half:double_pendulum. The h=0.05 and h=0.1 rows remain Newton failures after tolerance repair, and the repair grid/reference do not match the full HI2022 public-grid contract.
