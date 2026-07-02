# B2 Source-Policy Remaining Work Manifest

Status: `route_b_all_external_suites_demoted_no_active_external_superiority_rows`.

This is a read-only manifest over existing artifacts. It does not run new numerical experiments.

- Total flagged source-policy rows: `15`.
- Active flagged rows after Route B demotion: `0`.
- Demoted flagged rows after Route B demotion: `15`.
- Source-policy closed rows: `0`.
- External-superiority-ready rows: `0`.
- B2 closed by demotion: `['vp2024_code_resolution_or_demotion', 'hi2022_public_code_same_test_rows', 'ra2021_public_code_same_test_rows', 'original_tfe_pendulum_error_order_work_rows']`.
- B2 remaining requirements: `[]`.
- Route B B2/B4 claim-boundary synchronized: `True/True`.
- Route B B2/B4 closure ready pending gate sync: `False/False`.
- External superiority claim allowed: `False`.
- Default 1e-4/heavy/run_v047: `False/False/False`.
- Closure execution plan: `b2-source-policy-closure-execution-plan-v1`.
- Closure plan all active suites ready: `True`.
- Closure plan explicit 1e-4 opt-in required: `True`.
- Same-test acceptance contract: `same-test-source-policy-contract-v1`.
- Same-test contract closes rows now: `False`.
- TFE candidate full T=10 probe finite/residual/source-policy rows: `4/4/0`.
- TFE current disposition: `attempted_not_reproducible_not_promoted`; no public source-code-equivalent artifact was found.
- VP full source-policy rows unresolved/attempted/unable/closed: `4/4/4/0`; final disposition `unable_to_reproduce_not_promoted`.

## Suite Summary

| suite | active rows | demoted rows | status | next action |
|---|---:|---:|---|---|
| `ra2021_absolute_coordinate` | `0` | `5` | `closed_by_route_b_external_superiority_demotion` | keep as bounded public-code/common-reference diagnostic outside external-superiority scope |
| `hi2022_half_implicit` | `0` | `3` | `closed_by_explicit_source_policy_demotion` | keep as bounded diagnostic only after incomplete T=8 source-policy evidence |
| `tfe2026_original_pendulum` | `0` | `4` | `closed_by_attempted_not_reproducible_route_b_external_superiority_demotion` | keep as formal-order comparator and candidate diagnostic outside external-superiority scope |
| `vp2024_velocity_partitioning` | `0` | `3` | `closed_by_attempted_not_reproducible_route_b_external_superiority_demotion` | keep proxy evidence diagnostic; full VP source-policy rows are unable-to-reproduce/not-promoted until a new source-code-equivalent artifact appears |

## Row-Level Work Items

| # | suite | example | method | status | action |
|---:|---|---|---|---|---|
| 1 | `hi2022_half_implicit` | `four_link` | `hi2022_rA` | `closed_by_explicit_source_policy_demotion` | `demoted_after_incomplete_full_T8_source_policy_evidence` |
| 2 | `hi2022_half_implicit` | `double_pendulum` | `hi2022_rA_half` | `closed_by_explicit_source_policy_demotion` | `demoted_after_incomplete_full_T8_source_policy_evidence` |
| 3 | `hi2022_half_implicit` | `four_link` | `hi2022_rA_half` | `closed_by_explicit_source_policy_demotion` | `demoted_after_incomplete_full_T8_source_policy_evidence` |
| 4 | `ra2021_absolute_coordinate` | `single_pendulum` | `ra2021_rA` | `closed_by_route_b_external_superiority_demotion` | `route_b_demoted_keep_public_baseline_and_common_reference_diagnostics` |
| 5 | `ra2021_absolute_coordinate` | `four_link` | `ra2021_rA` | `closed_by_route_b_external_superiority_demotion` | `route_b_demoted_keep_public_baseline_and_common_reference_diagnostics` |
| 6 | `ra2021_absolute_coordinate` | `single_pendulum` | `ra2021_reps` | `closed_by_route_b_external_superiority_demotion` | `route_b_demoted_keep_public_baseline_and_common_reference_diagnostics` |
| 7 | `ra2021_absolute_coordinate` | `single_pendulum` | `ra2021_rp` | `closed_by_route_b_external_superiority_demotion` | `route_b_demoted_keep_public_baseline_and_common_reference_diagnostics` |
| 8 | `ra2021_absolute_coordinate` | `double_pendulum` | `ra2021_rp` | `closed_by_route_b_external_superiority_demotion` | `route_b_demoted_keep_public_baseline_and_common_reference_diagnostics` |
| 9 | `tfe2026_original_pendulum` | `single_pendulum` | `tfe2026_Newmark_beta` | `closed_by_attempted_not_reproducible_route_b_external_superiority_demotion` | `attempted_not_reproducible_not_promoted_keep_formula_comparator_and_candidate_diagnostics` |
| 10 | `tfe2026_original_pendulum` | `single_pendulum` | `tfe2026_TFE_m1` | `closed_by_attempted_not_reproducible_route_b_external_superiority_demotion` | `attempted_not_reproducible_not_promoted_keep_formula_comparator_and_candidate_diagnostics` |
| 11 | `tfe2026_original_pendulum` | `single_pendulum` | `tfe2026_TFE_m2` | `closed_by_attempted_not_reproducible_route_b_external_superiority_demotion` | `attempted_not_reproducible_not_promoted_keep_formula_comparator_and_candidate_diagnostics` |
| 12 | `tfe2026_original_pendulum` | `single_pendulum` | `tfe2026_trapezoidal` | `closed_by_attempted_not_reproducible_route_b_external_superiority_demotion` | `attempted_not_reproducible_not_promoted_keep_formula_comparator_and_candidate_diagnostics` |
| 13 | `vp2024_velocity_partitioning` | `single_pendulum` | `vp2024_coordinate_partitioning_rA` | `closed_by_attempted_not_reproducible_route_b_external_superiority_demotion` | `attempted_not_reproducible_not_promoted_keep_proxy_diagnostic` |
| 14 | `vp2024_velocity_partitioning` | `four_link` | `vp2024_coordinate_partitioning_rA` | `closed_by_attempted_not_reproducible_route_b_external_superiority_demotion` | `attempted_not_reproducible_not_promoted_keep_proxy_diagnostic` |
| 15 | `vp2024_velocity_partitioning` | `slider_crank` | `vp2024_coordinate_partitioning_rA` | `closed_by_attempted_not_reproducible_route_b_external_superiority_demotion` | `attempted_not_reproducible_not_promoted_keep_proxy_diagnostic` |

## Closure Execution Plan

| suite | ready to launch | explicit 1e-4 opt-in | plan-only closes B2 | key blocker |
|---|---:|---:|---:|---|
| `ra2021_absolute_coordinate` | `True` | `True` | `False` | `promote_or_rerun_local_Gauss6_FullVA_same_policy_dynamic_order_rows` |
| `tfe2026_original_pendulum` | `False` | `None` | `False` | `no_distinct_public_tfe_code_artifact_found` |

## Same-Test Acceptance Contract

| suite | cases | horizon/reference contract | required work metrics | acceptance rule |
|---|---|---|---|---|
| `ra2021_absolute_coordinate` | `single_pendulum`, `double_pendulum`, `four_link`, `slider_crank` | T=3 source-policy target; public output variables and source-bound norm/reference policy | `wall_time_sec`, `total_newton_iterations`, `jacobian_or_colored_derivative_time_sec`, `linear_solve_time_sec_if_available` | all four examples have promoted local Gauss6/FullVA rows or an explicit suite demotion; the promoted rows use the required horizon, h grid, reference, output norm, and solver policy; runtime/Newton metrics are tied to the same rows used for the order/error table; floor-limited or residual-only rows are not promoted to external superiority; accepted rows now `0` |
| `tfe2026_original_pendulum` | `frictionless_pendulum`, `frictional_revolute_joint_pendulum` | historical T=10 source pendulum contract retained only as a future condition if a source-code-equivalent artifact appears | `wall_time_sec`, `newton_iterations`, `jacobian_time_sec`, `source_reference_time_sec` | no source-policy row is promoted from the paper-spec/proxy reconstruction; a future promotion would require a new source-code-equivalent public or author artifact; any future source-equivalent artifact would need the friction law, endpoint/output policy, reference, error norm, and work metrics bound to the same rows; candidate coarse or formula-only rows remain diagnostic and are not external-superiority evidence; accepted rows now `0` |

Representative opt-in commands are stored in `B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json`.
They are not executed by this manifest, and rows involving `1e-4` require an explicit `--allow-source-policy-1e-4` flag.

The Route B demotions are claim-boundary decisions, not numerical wins.
TFE/VP rows with no usable public source-code-equivalent artifact are attempted-not-reproducible and not promoted.
RA2021 and HI2022 public-root diagnostics remain not-promoted until a source-policy promotion/execution closeout succeeds.
