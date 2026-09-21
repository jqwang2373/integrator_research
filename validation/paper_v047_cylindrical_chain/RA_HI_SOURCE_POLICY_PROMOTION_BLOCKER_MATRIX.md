# RA/HI Source-Policy Promotion Blocker Matrix

Status: `ra_hi_public_root_rows_not_promoted_source_policy_open`.

This is a read-only RA2021/HI2022 matrix. It excludes TFE/VP no-public-code rows and does not run guarded source-policy commands.

- Rows: `20`; RA/HI `12/8`.
- Public-source-root rows: `20`.
- No-public-code rows included: `0`.
- Direct aliases source-policy-closed/ratio/reproduction-complete: `False/0/20/False`.
- Direct aliases promoted/not-promoted/attempted-not-reproducible: `0/20/0`.
- Direct alias command-mapped/output-present: `20/20`; all present: `True`.
- Source-policy rows closed/promoted/not-promoted: `0/0/20`.
- Still requiring execution or promotion: `20`.
- Current-evidence terminal/not-promotable rows: `20`.
- Future promotion requires authorized execution or new artifact rows: `20`.
- Source-policy reproduction complete rows: `0`.
- Attempted-not-reproducible rows: `0`.
- Command-mapped/output-present rows: `20/20`.
- Ready after exact opt-in rows: `20`.
- Rows requiring explicit `1e-4` opt-in: `12`.
- Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.
- Safe action ids: `['rebuild_read_only_audit_chain', 'rerun_read_only_validators', 'keep_narrowed_archive_provenance_only', 'monitor_reopen_conditions']`; opt-in action ids: `['authorized_b4_ra_hi_source_policy_execution']`.
- Post-execution decision counts: `{'not_promoted': 20}`.
- Attempt status counts: `{'approved_driver_outputs_present_not_promoted': 9, 'diagnosis_only_low_order_floor_limited_not_promoted': 3, 'diagnosis_only_partial_newton_failure_not_promoted': 1, 'selected_candidate_executed_not_promoted': 7}`.
- Primary blocker counts: `{'hi2022_ra_half_double_partial_newton_failure_not_promoted': 1, 'hi2022_selected_coarse_trio_not_full_public_grid_not_promoted': 7, 'ra2021_closed_loop_T0p1_mixed_reference_not_source_policy': 6, 'ra2021_double_low_order_floor_limited_constraint_not_promoted': 3, 'ra2021_single_floor_limited_public_h_tranche_not_promoted': 3}`.
- Output inventory status/commands/outputs/closed: `existing_expected_outputs_present_not_promotion_evidence` / `13` / `13` / `0`.
- Closeout status: `ready_for_authorized_execution_closeout_not_executed_not_promoted`.
- Source-policy execution handoff exact approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh/True/True/13/20/20`.
- Source-policy execution handoff authorized/commands-not-run: `False/True`.
- B4/B7 can close now: `False/False`.
- Heavy/run_v047/v048 invoked: `False/False/False`.

## Suite Summary

| suite | rows | closed | not promoted | terminal current evidence | future authorization/new artifact | command mapped | output present | 1e-4 opt-in rows |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `hi2022_half_implicit` | `8` | `0` | `8` | `8` | `8` | `8` | `8` | `0` |
| `ra2021_absolute_coordinate` | `12` | `0` | `12` | `12` | `12` | `12` | `12` | `12` |

## Rows

| suite | method | example | attempt status | blocker | evidence | commands |
|---|---|---|---|---|---|---:|
| `hi2022_half_implicit` | `hi2022_rA` | `double_pendulum` | `selected_candidate_executed_not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` | `HI2022_SOURCE_POLICY_ROW_AUDIT.json` | `1` |
| `hi2022_half_implicit` | `hi2022_rA` | `four_link` | `selected_candidate_executed_not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` | `HI2022_SOURCE_POLICY_ROW_AUDIT.json` | `1` |
| `hi2022_half_implicit` | `hi2022_rA` | `single_pendulum` | `selected_candidate_executed_not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` | `HI2022_SOURCE_POLICY_ROW_AUDIT.json` | `1` |
| `hi2022_half_implicit` | `hi2022_rA` | `slider_crank` | `selected_candidate_executed_not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` | `HI2022_SOURCE_POLICY_ROW_AUDIT.json` | `1` |
| `hi2022_half_implicit` | `hi2022_rA_half` | `double_pendulum` | `diagnosis_only_partial_newton_failure_not_promoted` | `hi2022_ra_half_double_partial_newton_failure_not_promoted` | `HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json` | `1` |
| `hi2022_half_implicit` | `hi2022_rA_half` | `four_link` | `selected_candidate_executed_not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` | `HI2022_SOURCE_POLICY_ROW_AUDIT.json` | `1` |
| `hi2022_half_implicit` | `hi2022_rA_half` | `single_pendulum` | `selected_candidate_executed_not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` | `HI2022_SOURCE_POLICY_ROW_AUDIT.json` | `1` |
| `hi2022_half_implicit` | `hi2022_rA_half` | `slider_crank` | `selected_candidate_executed_not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` | `HI2022_SOURCE_POLICY_ROW_AUDIT.json` | `1` |
| `ra2021_absolute_coordinate` | `ra2021_rA` | `double_pendulum` | `diagnosis_only_low_order_floor_limited_not_promoted` | `ra2021_double_low_order_floor_limited_constraint_not_promoted` | `RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_rA` | `four_link` | `approved_driver_outputs_present_not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_rA` | `single_pendulum` | `approved_driver_outputs_present_not_promoted` | `ra2021_single_floor_limited_public_h_tranche_not_promoted` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_rA` | `slider_crank` | `approved_driver_outputs_present_not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_reps` | `double_pendulum` | `diagnosis_only_low_order_floor_limited_not_promoted` | `ra2021_double_low_order_floor_limited_constraint_not_promoted` | `RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_reps` | `four_link` | `approved_driver_outputs_present_not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_reps` | `single_pendulum` | `approved_driver_outputs_present_not_promoted` | `ra2021_single_floor_limited_public_h_tranche_not_promoted` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_reps` | `slider_crank` | `approved_driver_outputs_present_not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_rp` | `double_pendulum` | `diagnosis_only_low_order_floor_limited_not_promoted` | `ra2021_double_low_order_floor_limited_constraint_not_promoted` | `RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_rp` | `four_link` | `approved_driver_outputs_present_not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_rp` | `single_pendulum` | `approved_driver_outputs_present_not_promoted` | `ra2021_single_floor_limited_public_h_tranche_not_promoted` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_rp` | `slider_crank` | `approved_driver_outputs_present_not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |

Reading rule: these rows are public-root rows with existing diagnostic or candidate outputs, not no-public-code rows. Current evidence is terminal/not-promotable for all 20 rows, while source-policy reproduction remains incomplete. Future promotion requires either the exact B4 opt-in authorized execution closeout or a new source-policy promotion artifact.
