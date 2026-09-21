# B4 Source-Policy Execution Handoff Package

Status: `source_policy_execution_handoff_ready_not_authorized_not_run`.

This package is read-only. It does not authorize or run any B4 source-policy command.

- Source-policy rows closed/total: `0/40`.
- Terminal unable-to-reproduce rows: `20`.
- RA/HI rows requiring authorized closeout or new artifact: `20`.
- Ready command batches/commands/mapped rows: `2/13/20`.
- Command traceability unique RA/HI rows: `20/20`.
- Command traceability references/declared references/mismatches: `32/32/0`.
- Command traceability terminal rows/source-policy closed rows: `0/0`.
- Expected output schema audit: `expected_outputs_schema_ready_not_authorized_not_run_not_promoted`; commands/artifacts/hash-match/parseable/schema-ready/closed `13/21/21/13/13/0`.
- Expected output schema command traceability shell/output/summary/no-summary/existing-output/existing-summary: `13/13/8/5/13/8`.
- Execution authorized: `False`.
- Commands run by this handoff: `False`.
- Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.
- Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.
- Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.
- Post-execution promotion required: `True`.
- B4/B7 can close now: `False/False`.

## Terminal Unable-To-Reproduce Suites

| suite | rows | attempted | unable | closed |
|---|---:|---:|---:|---:|
| `tfe2026_original_pendulum` | `16` | `16` | `16` | `0` |
| `vp2024_velocity_partitioning` | `4` | `4` | `4` | `0` |

## Guarded Command Batches

| batch | commands | mapped rows | status | allow 1e-4 |
|---|---:|---:|---|---|
| `ra2021_ready_after_explicit_1e_4_opt_in` | `5` | `12` | `ready_not_run_requires_user_opt_in` | `True` |
| `hi2022_ready_no_1e_4_selected_candidate` | `8` | `8` | `preflight_ready_existing_selected_candidate_matrix_incomplete` | `None` |

## Command Row Traceability

| command | traced rows | declared rows | source-policy closed | promotion ready |
|---|---:|---:|---:|---:|
| `ra2021_public_timing_all_forms_models` | `12` | `12` | `0` | `0` |
| `gauss6_public_single_source_policy_trio` | `3` | `3` | `0` | `0` |
| `ra2021_double_order_all_forms` | `3` | `3` | `0` | `0` |
| `gauss6_public_four_link_source_policy_trio` | `3` | `3` | `0` | `0` |
| `gauss6_public_slider_crank_source_policy_trio` | `3` | `3` | `0` | `0` |
| `hi2022_selected_t8_rA_half_single_pendulum` | `1` | `1` | `0` | `0` |
| `hi2022_selected_t8_rA_half_double_pendulum` | `1` | `1` | `0` | `0` |
| `hi2022_selected_t8_rA_half_four_link` | `1` | `1` | `0` | `0` |
| `hi2022_selected_t8_rA_half_slider_crank` | `1` | `1` | `0` | `0` |
| `hi2022_selected_t8_rA_single_pendulum` | `1` | `1` | `0` | `0` |
| `hi2022_selected_t8_rA_double_pendulum` | `1` | `1` | `0` | `0` |
| `hi2022_selected_t8_rA_four_link` | `1` | `1` | `0` | `0` |
| `hi2022_selected_t8_rA_slider_crank` | `1` | `1` | `0` | `0` |

## Exact Opt-In Boundary

`I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`

Even after authorized execution, rows are not closed until the post-execution promotion audit and validators promote them.
