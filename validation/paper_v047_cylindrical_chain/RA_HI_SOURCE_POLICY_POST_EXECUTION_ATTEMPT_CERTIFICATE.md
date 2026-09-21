# RA/HI Source-Policy Post-Execution Attempt Certificate

Status: **post-execution attempts recorded; rows not promoted; full source-policy open**.

- Rows audited: `20`.
- RA2021/HI2022 rows: `12/8`.
- Source-policy rows promoted: `0`.
- External-superiority ready rows: `0`.
- Rows still requiring execution or promotion: `20`.
- Source-policy closed/total: `0/40`.
- Heavy/run_v047/v048 invoked: `False/False/False`.
- Submission ready: `False`.
- Verified authorized B4 execution recorded: `False`.
- Existing ready-command artifacts present: `True`.
- Execution record scope: `no_verified_current_authorized_execution_record_existing_artifacts_only`.
- Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.
- Required approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh`.
- Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.
- Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.

## Promotion Blockers

| blocker | rows |
|---|---:|
| `hi2022_ra_half_double_partial_newton_failure_not_promoted` | `1` |
| `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` | `7` |
| `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` | `6` |
| `ra2021_double_low_order_floor_limited_constraint_not_promoted` | `3` |
| `ra2021_single_floor_limited_public_h_tranche_not_promoted` | `3` |

## Evidence Summary

- RA2021 public order/timing groups: `12/12`.
- RA2021 double candidate pos/vel order and promoted rows: `2.148/2.463/0`.
- HI2022 selected candidate completed/expected shards and ok/total rows: `7/8` and `22/24`.
- HI2022 rA_half double ok/failed/Newton-failure/promoted rows: `1/2/2/0`.
- HI2022 rA_half double repair target ok/failed and combined ok/rows/groups: `1/2` and `19/24/4/8`.

## Row Disposition

| suite | method | example | status | primary blocker |
|---|---|---|---|---|
| `hi2022_half_implicit` | `hi2022_rA` | `double_pendulum` | `selected_candidate_executed_not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` |
| `hi2022_half_implicit` | `hi2022_rA` | `four_link` | `selected_candidate_executed_not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` |
| `hi2022_half_implicit` | `hi2022_rA` | `single_pendulum` | `selected_candidate_executed_not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` |
| `hi2022_half_implicit` | `hi2022_rA` | `slider_crank` | `selected_candidate_executed_not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` |
| `hi2022_half_implicit` | `hi2022_rA_half` | `double_pendulum` | `diagnosis_only_partial_newton_failure_not_promoted` | `hi2022_ra_half_double_partial_newton_failure_not_promoted` |
| `hi2022_half_implicit` | `hi2022_rA_half` | `four_link` | `selected_candidate_executed_not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` |
| `hi2022_half_implicit` | `hi2022_rA_half` | `single_pendulum` | `selected_candidate_executed_not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` |
| `hi2022_half_implicit` | `hi2022_rA_half` | `slider_crank` | `selected_candidate_executed_not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` |
| `ra2021_absolute_coordinate` | `ra2021_rA` | `double_pendulum` | `diagnosis_only_low_order_floor_limited_not_promoted` | `ra2021_double_low_order_floor_limited_constraint_not_promoted` |
| `ra2021_absolute_coordinate` | `ra2021_rA` | `four_link` | `approved_driver_outputs_present_not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` |
| `ra2021_absolute_coordinate` | `ra2021_rA` | `single_pendulum` | `approved_driver_outputs_present_not_promoted` | `ra2021_single_floor_limited_public_h_tranche_not_promoted` |
| `ra2021_absolute_coordinate` | `ra2021_rA` | `slider_crank` | `approved_driver_outputs_present_not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` |
| `ra2021_absolute_coordinate` | `ra2021_reps` | `double_pendulum` | `diagnosis_only_low_order_floor_limited_not_promoted` | `ra2021_double_low_order_floor_limited_constraint_not_promoted` |
| `ra2021_absolute_coordinate` | `ra2021_reps` | `four_link` | `approved_driver_outputs_present_not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` |
| `ra2021_absolute_coordinate` | `ra2021_reps` | `single_pendulum` | `approved_driver_outputs_present_not_promoted` | `ra2021_single_floor_limited_public_h_tranche_not_promoted` |
| `ra2021_absolute_coordinate` | `ra2021_reps` | `slider_crank` | `approved_driver_outputs_present_not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` |
| `ra2021_absolute_coordinate` | `ra2021_rp` | `double_pendulum` | `diagnosis_only_low_order_floor_limited_not_promoted` | `ra2021_double_low_order_floor_limited_constraint_not_promoted` |
| `ra2021_absolute_coordinate` | `ra2021_rp` | `four_link` | `approved_driver_outputs_present_not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` |
| `ra2021_absolute_coordinate` | `ra2021_rp` | `single_pendulum` | `approved_driver_outputs_present_not_promoted` | `ra2021_single_floor_limited_public_h_tranche_not_promoted` |
| `ra2021_absolute_coordinate` | `ra2021_rp` | `slider_crank` | `approved_driver_outputs_present_not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` |

The RA2021 and HI2022 rows have post-driver evidence, but each row remains blocked by low-order/floor-limited behavior, residual-only or mixed-reference coverage, incomplete public-grid execution, partial Newton failure, or missing error/runtime/Newton work binding.
