# RA2021 Double Source-Policy Low-Order Diagnosis

Status: **diagnosis only; low-order rows are not promoted**.

This artifact reads the completed isolated candidate rows and does not invoke any numerical runner.

- Candidate summary status: `executed_isolated_source_policy_candidate`.
- Rows complete: `True` with `3` rows.
- Source-policy h/ref contract selected: `True`.
- Generic RA2021 public h represented as candidate rows: `2/3`.
- Non-public selected candidate h values: `[0.002]`.
- Aggregate pos/vel order: `2.148/2.463` below threshold `5.500`.
- Coarse-to-mid 0.01 -> 0.002 pos/vel order: `2.825/3.248`.
- Fine pair floor-limited: `True`.
- Fine pair 0.002 -> 0.001 pos/vel order: `0.097/0.084`.
- h=0.01 constraint threshold satisfied: `False`.
- Single implementation defect proven by this diagnosis: `False`.
- Coarse h constraint failure components: `['endpoint_velocity_constraint']`.
- Fine-pair floor margin to threshold: `0.176` with finest/reference h ratio `10.000`.
- Ledger binding reconciliation: local metrics present `True`, accepted binding `False`, ledger RA2021 remaining evidence per row `4`, row status shrink `False`.
- Promotion ready: `False`.
- Source-policy rows promoted by this diagnosis: `0`.
- B4/B7 can close from this diagnosis: `False`.

## Pairwise Orders

| pair | h ratio | pos ratio | vel ratio | pos order | vel order | floor-limited |
|---|---:|---:|---:|---:|---:|---:|
| `0.01_to_0.002` | `5.000` | `94.280` | `186.338` | `2.825` | `3.248` | `False` |
| `0.002_to_0.001` | `2.000` | `1.069` | `1.060` | `0.097` | `0.084` | `True` |

## Final-vs-Trajectory Order Sensitivity

| metric | pair | error ratio | pair order |
|---|---|---:|---:|
| `pos_traj_linf` | `0.01_to_0.002` | `94.280` | `2.825` |
| `vel_traj_linf` | `0.01_to_0.002` | `186.338` | `3.248` |
| `pos_final_linf` | `0.01_to_0.002` | `80.234` | `2.725` |
| `vel_final_linf` | `0.01_to_0.002` | `40.379` | `2.298` |
| `pos_traj_linf` | `0.002_to_0.001` | `1.069` | `0.097` |
| `vel_traj_linf` | `0.002_to_0.001` | `1.060` | `0.084` |
| `pos_final_linf` | `0.002_to_0.001` | `1.219` | `0.286` |
| `vel_final_linf` | `0.002_to_0.001` | `1.060` | `0.084` |

## Rows

| h | status | source h | public h | pos traj linf | vel traj linf | constraint threshold | Newton iterations | runtime sec |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `0.010` | `ok` | `True` | `True` | `2.839e-11` | `3.270e-10` | `False` | `1155` | `110.505` |
| `2.000e-03` | `ok` | `True` | `False` | `3.011e-13` | `1.755e-12` | `True` | `4680` | `278.752` |
| `1.000e-03` | `ok` | `True` | `True` | `2.816e-13` | `1.656e-12` | `True` | `9000` | `553.477` |

## Decision

The exact h/ref source-policy candidate rows are complete, but the aggregate order is below acceptance, the 0.01->0.002 pair is itself below sixth-order acceptance, the 0.002->0.001 pair is near the numerical floor, the h=0.01 row misses the constraint threshold, the scope remains an isolated local double source-policy candidate rather than the generic RA2021 public order step family, and independent rerun plus error/runtime/Newton bindings remain absent.

These rows remain a root-cause diagnostic for B4/B7, not row-closure or external-superiority evidence.
