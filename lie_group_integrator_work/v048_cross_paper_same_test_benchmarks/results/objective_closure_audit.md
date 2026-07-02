# Objective Closure Audit

Objective complete: `True`.
Passed requirements: `13/13`.
Step sizes: `[0.1, 0.05, 0.025]`; reference h: `0.0125`.

## Local Orders

| Example | pos order | vel order | acc order | finest vel error |
|---|---:|---:|---:|---:|
| `single_pendulum` | `6.0128039157529658e+00` | `5.8013285781956512e+00` | `5.0559023369543672e+00` | `1.1551877762897842e-12` |
| `double_pendulum` | `6.0107116196912500e+00` | `6.0097049897199657e+00` | `nan` | `2.3455890008072799e-13` |
| `four_link` | `5.9548979111188078e+00` | `6.0848187309877098e+00` | `9.9466887815859806e-01` | `1.0927703186780491e-11` |
| `slider_crank` | `6.1636896425143544e+00` | `7.3409145102638718e+00` | `1.0541648128408896e+00` | `9.1888510689308589e-12` |

## Direct Wins

- Apples-to-apples policy rows: `44/44`.
- Global comparison-policy audit: `13/13`.
- Mixed-policy direct error rows allowed: `0`.
- Source-policy reproduction: `False`.
- Public-code fixed-grid replay: `True`.
- Local velocity-order wins: `40/40`.
- Local finest-velocity-error wins: `40/40`.
- Original-paper velocity-error wins: `16/16`.
- Kissel/Negrut-family velocity-error wins: `24/24`.

## Requirement Audit

| Requirement | status | evidence | interpretation |
|---|---:|---|---|
| `four_named_examples_present` | `pass` | `coarse_four_example_order_summary.json; common_reference_error_summary.json` | single, double, four-link, and slider-crank examples are all present for the local method and common-reference audit |
| `shared_coarse_step_sizes` | `pass` | `coarse_four_example_order_summary.json; common_reference_error_summary.json` | all accepted comparison rows use h = 0.1, 0.05, 0.025 |
| `coarse_reference_policy` | `pass` | `coarse_four_example_order_summary.json; common_reference_error_summary.json` | the comparison uses reference h = 0.0125 rather than default 1e-4 |
| `apples_to_apples_policy_audit` | `pass` | `apples_to_apples_policy_audit.json` | all four examples and all accepted methods pass the shared h-grid/reference/norm audit; public-code rows use fixed-grid replay |
| `global_comparison_policy_audit` | `pass` | `global_comparison_policy_audit.json` | all claim-bearing comparison artifacts pass the global apples-to-apples/claim-boundary audit |
| `required_methods_resolved` | `pass` | `baseline_coverage_matrix.json` | all required method labels are accepted, alias-resolved, or source-backed scope-excluded |
| `vp_alias_resolved` | `pass` | `vp_method_identity_audit.json` | VP Lie-group ODE partitioning is treated as the implemented coordinate-partitioning wrapper |
| `tfe_m3_scope_excluded` | `pass` | `tfe_m3_scope_exclusion_audit.json` | TFE(m=3) four-link is a source-backed excluded stress row, not a required accepted baseline |
| `direct_common_reference_error_wins` | `pass` | `common_reference_error_summary.json` | local method has lower finest-step velocity error on all 40 direct common-reference nonlocal comparisons |
| `direct_common_reference_order_wins` | `pass` | `common_reference_error_summary.json` | local method has higher velocity order on all 40 direct common-reference nonlocal comparisons |
| `original_paper_error_wins` | `pass` | `common_reference_error_summary.json` | local method has lower finest-step velocity error than accepted original-paper baseline rows |
| `kissel_negrut_error_wins` | `pass` | `common_reference_error_summary.json` | local method has lower finest-step velocity error than accepted Kissel/Negrut-family baseline rows |
| `order_and_error_tables_written` | `pass` | `results directory` | raw/summary CSVs and order/error figures are present |

The active comparison objective is complete for the required method matrix: all required labels are accepted/alias-resolved/source-backed excluded; all four examples use the coarse h trio under explicit row-level and global apples-to-apples policy audits; public-code baselines are fixed-grid replayed rather than source-policy reproduced; mixed-policy direct error claims are blocked; and the local method wins all direct common-reference velocity-error and velocity-order comparisons against accepted original-paper and Kissel/Negrut-family rows.
