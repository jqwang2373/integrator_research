# HI2022 Full T=8 Source-Policy Candidate

Status: **executed_full_T8_selected_coarse_trio_not_promoted**.

- Execution phase: `candidate`.
- Form/model: `rA_half` / `slider_crank`.
- T=8 time window selected: `True`.
- Reference h selected: `True`.
- Selected step sizes: `[0.02, 0.01, 0.005]`.
- Full public grid selected: `False`.
- Source-policy 1e-4 included: `False`.
- Rows ok/total: `3/3`.
- Selected step trio completed: `True`.
- Position pair orders: `[3.24906198377441, 0.0791438847197366]`.
- Velocity pair orders: `[0.9985830190096858, 0.9996582944124607]`.
- Acceleration pair orders: `[1.0056582034571655, 1.0055390633370984]`.
- Runtime values: `[0.6810450529446825, 1.1745680769672617, 1.8977922629565]`.
- Reference runtime: `15.855694137047976`.
- Full T=8 policy completed: `False`.
- Source-policy rows promoted: `0`.
- Source-policy rows closed by this evidence: `0`.
- Promotion ready: `False`.
- B4/B7 can close from this candidate: `False/False`.
- Canonical HI2022 output untouched by this writer: `True`.

Promotion blockers:
- full HI2022 public step grid is not selected or not completed
- work/precision figure rows are not promoted from this isolated shard
- runtime and error/order rows are not yet bound into a publication-grade full-policy figure
- selected coarse trio is not the full encoded HI2022 public step family

This candidate can document T=8 executability for one shard, but it is not a full HI2022 source-policy work/precision curve.
It closes zero B4/B7 source-policy rows unless the full policy grid, tied work metrics, and figure-scope decision are promoted by a separate audited step.
