# Current Coarse-Grid Conclusion

Status: **bounded_table_assembled_source_policy_open**.

This is the current defensible claim from the shared four-example coarse grid. It uses h = 0.1, 0.05, 0.025 and reference h = 0.0125; it does not use a default 1e-4 run.

## Forensic Audit Override

- All method/example cells checked: `44/44`.
- Strict external error-claim rows allowed: `0`.
- Direct error superiority allowed for paper: `False`.
- Source-policy reproduction: `False`.

The common-reference numbers below are bounded diagnostics. They do not close the source-paper apples-to-apples comparison because source-policy reproduction, velocity/output mapping, original TFE setup, and VP code-path questions remain open.

## Local Method

| Example | pos order | vel order | acc order | finest vel error |
|---|---:|---:|---:|---:|
| `double_pendulum` | `6.0107116196912500e+00` | `6.0097049897199657e+00` | `nan` | `2.3455890008072799e-13` |
| `four_link` | `5.9548979111188078e+00` | `6.0848187309877098e+00` | `9.9466887815859806e-01` | `1.0927703186780491e-11` |
| `single_pendulum` | `6.0128039157529658e+00` | `5.8013285781956512e+00` | `5.0559023369543672e+00` | `1.1551877762897842e-12` |
| `slider_crank` | `6.1636896425143544e+00` | `7.3409145102638718e+00` | `1.0541648128408896e+00` | `9.1888510689308589e-12` |

## Comparison Claim

- Velocity order: local wins `43/43` finite runnable comparisons.
- Reported velocity error: local wins `40/43` finite runnable comparisons under each row's own reference policy.
- Position error: local wins `20/43` finite runnable comparisons; these rows are contaminated by constrained-kinematic and reference-floor effects, so they are not the primary superiority claim.

The present main claim should therefore be velocity-order superiority, not a blanket position-error or every-error superiority claim. With the all-example forensic audit active, common-reference error wins are bounded diagnostics rather than paper-level external-superiority evidence.

## Reference Policy Boundary

- Observed-order comparable rows: `43`.
- Direct error-vs-local comparable rows: `40`.
- Common-reference local velocity-order wins: `40/40`.
- Common-reference local finest-velocity-error wins: `40/40`.
- Paper-level direct error superiority allowed: `False`.

The main table's error columns are reported errors under mixed reference policies. Direct cross-method error claims should use the common-reference audit section below, but the forensic audit decides whether those rows are strong enough for a paper claim.

## Velocity-Error Loss Rows

| Example | method | method vel order | local vel order | vel error ratio vs local |
|---|---|---:|---:|---:|
| `four_link` | `vp2024_coordinate_partitioning_rA` | `9.2663231296479098e-01` | `6.0848187309877098e+00` | `2.1725525257040679e-01` |
| `single_pendulum` | `vp2024_coordinate_partitioning_rA` | `2.7082010409952339e-15` | `5.8013285781956512e+00` | `4.8053790362591748e-05` |
| `slider_crank` | `vp2024_coordinate_partitioning_rA` | `6.6050359651248636e-01` | `7.3409145102638718e+00` | `1.0650532790939495e-02` |

These losses are all against the VP2024 coordinate-partitioning rA wrapper. The coarse-grid rows alone are not enough to dismiss them as only a floor artifact. A larger-step audit is therefore used below to check whether the order gap survives away from the original h = 0.1/0.05/0.025 grid.

## Larger-Step VP Audit

To test whether the VP coordinate-partitioning order was artificially depressed by the original fine/coarse grid, a diagnostic audit uses h = 0.15, 0.075, 0.0375, reference h = 0.01875, and t_end = 0.15.

- Comparable examples: `4/4`.
- Local velocity-order wins: `4/4`.
- Local finest-velocity-error wins: `1/4`.

| Example | local vel order | VP vel order | local reported finest vel error | VP reported finest vel error |
|---|---:|---:|---:|---:|
| `single_pendulum` | `6.0135643426036260e+00` | `-3.5286613417865970e-15` | `1.4182787749464959e-11` | `1.1102230246251565e-16` |
| `double_pendulum` | `6.0090107704951414e+00` | `1.4037663832547063e+00` | `5.0263508633019427e-12` | `3.6540878301565480e-03` |
| `four_link` | `5.0528931248450188e+00` | `1.6484873456452285e+00` | `4.7075232600946038e-11` | `4.4932946252629336e-12` |
| `slider_crank` | `6.3108972490961275e+00` | `1.0626008446907540e+00` | `1.6179349388023567e-09` | `3.1173674752693614e-13` |

This larger-step audit supports the order claim but tightens the error claim: local remains higher-order on all four VP-coordinate rows, while VP still has the smaller reported finest-step velocity error on three of four rows under mixed reference policies. Therefore the defensible statement is higher observed order, not lower common-reference error everywhere.

## Common-Reference Error Audit

For direct error superiority, a separate audit reruns the accepted runnable methods and compares final states against one shared reference and norm per example.

- Direct comparable nonlocal rows: `40`.
- Local velocity-order wins: `40/40`.
- Local finest-velocity-error wins: `40/40`.
- Original-paper finest-velocity-error wins: `16/16`.
- Kissel/Negrut-family finest-velocity-error wins: `24/24`.
- Bounded direct all-row error diagnostic over accepted runnable rows: `True`.
- Paper-level direct error superiority allowed after all-example forensic audit: `False`.

| Example | local vel order | worst nonlocal vel order | local finest vel error | nearest nonlocal finest vel error |
|---|---:|---:|---:|---:|
| `single_pendulum` | `5.8013285781956512e+00` | `6.1493372218877035e-15` | `1.1551877762897842e-12` | `3.1628033526739321e-11` |
| `double_pendulum` | `6.0097049897199657e+00` | `-7.9899483617845046e-01` | `2.3455890008072799e-13` | `4.9241208753159071e-05` |
| `four_link` | `6.0848187309877098e+00` | `-5.3315082332409090e-04` | `1.0927703186780491e-11` | `1.0874561251483783e-08` |
| `slider_crank` | `7.3409145102638718e+00` | `-3.2531547519751702e-07` | `9.1888510689308589e-12` | `1.3318257655048349e-07` |

This supports a bounded common-reference diagnostic for the 11 accepted runnable methods. It is not a final source-paper external-superiority statement. It excludes the source-backed TFE(m=3) four-link stress row, keeps the VP Lie-group ODE-partitioning label as an alias of the VP coordinate-partitioning wrapper, and leaves the all-example source-policy audit open.

## Resolved Alias

| Method | resolved as | note |
|---|---|---|
| `vp2024_lie_group_ode_partitioning` | `vp2024_coordinate_partitioning_rA` | The ASME 2023 VP DOI metadata describes independent-coordinate integration, dependent-coordinate recovery through position/velocity constraints, and Lie-group updates of orientation matrix A, matching the implemented wrapper. |

## Scope-Excluded Stress Rows

| Example | method | status | note |
|---|---|---:|---|
| `double_pendulum` | `tfe2026_TFE_m3_GL` | `ok` | TFE(m=3) Gauss-Lobatto Appendix B nu=0.9; setup tolerance=1.0e-10; multi-node solver tolerance=1.0e-08; multi-node finite-difference Newton wrapper from Algorithm 1. |
| `four_link` | `tfe2026_TFE_m3_GL` | `reference_failed` | TFE(m=3) Gauss-Lobatto Appendix B nu=0.9; strict reference skipped after targeted h=0.00625 failed at t=0.038 with residual=1.443e-04 and least_squares_residual=8.092e-05; strict h=0.0125 and relaxed tolerances 1e-4/5e-5 exceeded the smoke-test time budget. Common-reference candidate smoke at h=0.1/0.05/0.025 gives negative observed orders (-14.203 position; -10.560 velocity; -7.169 acceleration); so these rows are rejected as wrong-branch/stage-solve evidence. See results/tfe_m3_four_link_solver_audit.csv. This row is not used for order. |
| `single_pendulum` | `tfe2026_TFE_m3_GL` | `ok` | TFE(m=3) Gauss-Lobatto Appendix B nu=0.9; setup tolerance=1.0e-10; multi-node solver tolerance=1.0e-08; multi-node finite-difference Newton wrapper from Algorithm 1. |
| `slider_crank` | `tfe2026_TFE_m3_GL` | `ok` | TFE(m=3) Gauss-Lobatto Appendix B nu=0.9; setup tolerance=1.0e-10; multi-node solver tolerance=1.0e-08; multi-node finite-difference Newton wrapper from Algorithm 1. |

## Still Incomplete

| item | status |
|---|---|
| all-example source-policy reproduction | `False` |
| paper-level direct error superiority | `False` |
| RA2021/HI2022 velocity-output mapping and source policy | `open` |
| original TFE setup/error/output policy | `open` |
| VP2024 independent code path | `open` |

The bounded coarse error/order table is assembled, but the CMAME-level source-paper comparison is not closed. The current defensible claim is bounded observed-order evidence for the local method, not final external error superiority over all source-paper methods.
