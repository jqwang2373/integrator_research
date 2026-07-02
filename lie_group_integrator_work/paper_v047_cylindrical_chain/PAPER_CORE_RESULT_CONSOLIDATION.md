# Paper Core Result Consolidation

Status: **paper core results consolidated; replay-only, no experiment campaign**.

- Four-example local order: `4/4`.
- Common-reference order/error wins: `40/40` and `40/40`.
- Closed-loop coarse dynamics candidates: `2/2`.
- Core figures available: `True`.
- Direct PC2 proof gap closed: `True`.
- Direct PC2 proof-gap scope: `direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`.
- Schema-only compatibility key `proof_gap_closed` retained: `True`; reader-facing proof status should use `direct_pc2_proof_gap_closed`.
- Primitive 162-term Taylor route closed: `False`.
- Submission ready: `False`.
- Experiments launched: `False`.

## Four-Example Local Order

| example | velocity order | finest velocity error |
|---|---:|---:|
| `single pendulum` | `5.801` | `1.155e-12` |
| `double pendulum` | `6.010` | `2.346e-13` |
| `four-link` | `6.085` | `1.093e-11` |
| `slider-crank` | `7.341` | `9.189e-12` |

## Closed-Loop True-Dynamic Coarse Order

| example | position | orientation | velocity | omega | accepted |
|---|---:|---:|---:|---:|---|
| `four-link` | `5.955` | `5.955` | `6.085` | `5.971` | `True` |
| `slider-crank` | `6.164` | `6.159` | `7.341` | `6.426` | `True` |

## Core Figures

| no. | role | path |
|---:|---|---|
| `1` | accepted-path convergence and work/precision | `figures/convergence.png` |
| `7` | strict common-reference work/precision | `figures/strict_common_reference_work_precision.png` |
| `9` | coarse-first baseline/work-precision | `figures/coarse_baseline_work_precision.png` |
| `10` | closed-loop coarse dynamics diagnostics | `figures/closed_loop_true_dynamic_order.png` |
| `12` | all-method all-example result matrix | `figures/all_method_result_matrix.png` |

## Claim Boundary

- Allowed: Gauss6/FullVA achieves about sixth-order velocity convergence on the four paper examples and wins all bounded common-reference nonlocal order/error comparisons against accepted runnable rows.
- Allowed: four-link and slider-crank have closed-loop coarse dynamics diagnostic evidence with no stage oracle.
- Forbidden: strict source-paper policy external superiority; source-policy apples-to-apples closure; unconditional dynamic-row proof closure; submission-ready status.

Reading rule: this file is the non-policy paper-core result map. It consolidates existing artifacts only and does not promote source-policy, proof, or submission-readiness claims.
