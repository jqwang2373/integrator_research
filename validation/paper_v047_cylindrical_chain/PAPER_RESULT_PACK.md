# Paper Result Pack

Status: **claim-boundary result consolidation, not submission-ready acceptance**.

- Accepted method: `Gauss6/FullVA`.
- Accepted method order: `6`.
- Smooth projected orders: `7.161/7.066` position/velocity.
- ASME examples: `single_pendulum, double_pendulum, four_link, slider_crank`.
- Common-reference apples-to-apples rows: `44/44`.
- Global comparison-policy audit: `14/14`.
- Mixed-policy direct error rows allowed: `0`.
- Paper direct error rows allowed: `0`.
- All method/example cells checked: `44`.
- Source-policy reproduction: `False`.
- Public-code fixed-grid replay: `True`.
- External superiority claim: `False`.
- Submission ready: `False`.
- Global objective complete: `False`.
- Global submission ready: `False`.
- Global open blockers: `OC4, OC6, OC12`.
- Source-policy rows closed: `0/40`.
- v048 objective scope: `v048_cross_paper_fixed_grid_comparison_scaffold_only`.
- v048 objective global effect: `does_not_close_global_submission_ready`.
- Global quality review passed: `False`.
- Narrowed-claim quality review passed: `True`.
- Narrowed-claim decision alias: `submit_under_narrowed_claim` (legacy compatibility field for the bounded subcheck only; not a global submit instruction).

## Objective Blocker Matrix

This result pack consolidates paper evidence. It does not close the global objective blockers.

- `blocker_open_by_id=OC4:True,OC6:True,OC12:True`
- `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`
- `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`

## Common-Reference Velocity Evidence

| Example | local order | local finest error | nearest nonlocal method | nearest nonlocal error | strongest nonlocal order | weakest nonlocal order |
|---|---:|---:|---|---:|---:|---:|
| `single_pendulum` | `5.801` | `1.155e-12` | `vp2024_coordinate_partitioning_rA` | `3.163e-11` | `hi2022_rA_half 1.841` | `vp2024_coordinate_partitioning_rA 0.000` |
| `double_pendulum` | `6.010` | `2.346e-13` | `ra2021_rA` | `4.924e-05` | `tfe2026_trapezoidal 2.000` | `hi2022_rA_half -0.799` |
| `four_link` | `6.085` | `1.093e-11` | `vp2024_coordinate_partitioning_rA` | `1.087e-08` | `tfe2026_trapezoidal 3.888` | `vp2024_coordinate_partitioning_rA -0.001` |
| `slider_crank` | `7.341` | `9.189e-12` | `vp2024_coordinate_partitioning_rA` | `1.332e-07` | `tfe2026_TFE_m1 2.481` | `vp2024_coordinate_partitioning_rA -0.000` |

## All Runnable Method Rows

Each cell is `observed velocity order / finest-step velocity error` on the shared fixed-grid `h={0.1,0.05,0.025}` sweep with reference `h=0.0125`.

| Method | single_pendulum | double_pendulum | four_link | slider_crank |
|---|---:|---:|---:|---:|
| `local_Gauss6_FullVA` | `5.801 / 1.155e-12` | `6.010 / 2.346e-13` | `6.085 / 1.093e-11` | `7.341 / 9.189e-12` |
| `hi2022_rA` | `1.005 / 0.077` | `1.049 / 4.944e-05` | `1.015 / 0.197` | `0.941 / 0.033` |
| `hi2022_rA_half` | `1.841 / 0.077` | `-0.799 / 2.970` | `1.590 / 0.197` | `2.459 / 0.033` |
| `ra2021_rA` | `0.617 / 13.049` | `1.052 / 4.924e-05` | `1.015 / 0.197` | `0.941 / 0.033` |
| `ra2021_reps` | `0.617 / 13.049` | `1.052 / 4.924e-05` | `2.894 / 0.015` | `0.940 / 0.033` |
| `ra2021_rp` | `0.517 / 14.990` | `0.361 / 5.241e-05` | `2.894 / 0.015` | `0.940 / 0.033` |
| `tfe2026_Newmark_beta` | `0.901 / 14.791` | `1.787 / 4.246e-04` | `1.872 / 0.017` | `2.051 / 1.531e-03` |
| `tfe2026_TFE_m1` | `1.021 / 14.982` | `1.996 / 2.708e-04` | `3.866 / 5.253e-04` | `2.481 / 6.264e-04` |
| `tfe2026_TFE_m2` | `0.054 / 110.220` | `1.870 / 8.711e-05` | `1.021 / 6.711e-04` | `2.290 / 9.881e-05` |
| `tfe2026_trapezoidal` | `1.024 / 14.983` | `2.000 / 2.708e-04` | `3.888 / 5.306e-04` | `2.329 / 7.328e-04` |
| `vp2024_coordinate_partitioning_rA` | `0.000 / 3.163e-11` | `1.000 / 2.165e-03` | `-0.001 / 1.087e-08` | `-0.000 / 1.332e-07` |

## Claim Boundary

The accepted paper claim is an order-six Gauss6/FullVA method claim with four-example validation and a bounded fixed-grid common-reference diagnostic. It is not source-policy reproduction, not paper-level direct error superiority, not a full TFE replacement, and not a full external superiority claim.

The fixed-grid common-reference matrix is a bounded diagnostic. The all-example forensic audit allows zero paper-level direct error rows. The main mixed-policy coarse table supports observed-order comparisons and diagnostics, not blanket cross-method error superiority.

## Proof And Review Status

- Direct PC2 proof gap closed: `True`.
- Direct proof gap scope: `direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`.
- Direct proof gap reading rule: The schema-only compatibility boolean proof_gap_closed is a schema-compatible shorthand for direct_pc2_proof_gap_closed and is scoped to the active direct PC2 residual-bridge/Kantorovich proof closure. Reader-facing proof status should use direct_pc2_proof_gap_closed. The compatibility boolean does not close the primitive/Taylor route, P6 solver-policy evidence, P7 residual-to-error promotion, source-policy readiness, full-TFE replacement, or global submission readiness.
- Finite-run order-six scale evidence: `True`.
- Finite scaled-tolerance probe rows/max eta-h ratio: `4/4` / `127.583723`.
- Scaled solver tolerance evidence: `False`.
- Runtime AD formula-row oracle complete: `True`.
- Dynamic symbolic oracle complete: `False`.
- Symbolic row oracle complete: `False`.
- Symbolic-certificate stage residual `O(h^7)` route proved: `False`.
- Direct-route stage residual `O(h^7)` implementation defect proved: `True`.
- Narrowed-claim B-gate open blockers: ``.
- Narrowed-claim B-gate closed blockers: `B1, B2, B3, B4, B5, B6, B7, B8`.
- Global submission open blockers: `OC4, OC6, OC12`.
