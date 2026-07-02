# HI2022 Full T=8 Source-Policy Candidate

Status: **executed_full_T8_selected_coarse_trio_not_promoted**.

- Execution phase: `candidate`.
- Form/model: `rA` / `four_link`.
- T=8 time window selected: `True`.
- Reference h selected: `True`.
- Selected step sizes: `[0.02, 0.01, 0.005]`.
- Full public grid selected: `False`.
- Source-policy 1e-4 included: `False`.
- Rows ok/total: `3/3`.
- Selected step trio completed: `True`.
- Position pair orders: `[0.45711722252133086, -0.3949107994269268]`.
- Velocity pair orders: `[1.0029529977079763, 1.0015593303001036]`.
- Acceleration pair orders: `[1.020314858981941, 1.0100160558274491]`.
- Runtime values: `[1.7729512569494545, 2.895835777046159, 4.014201128971763]`.
- Reference runtime: `16.873604504973628`.
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
