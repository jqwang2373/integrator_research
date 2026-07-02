# Full Source-Policy Row Provenance Audit

Status: `row_provenance_preflight_complete_source_policy_promotion_open`.

This read-only audit does not execute B4, v048, or heavy numerical commands.
It records row-level provenance preflight only; provenance preflight is not source-policy promotion.

## Summary

- Rows: `40/40`.
- Provenance preflight complete rows: `40/40`.
- Public-source-root rows: `20`.
- Unable-to-reproduce rows: `20`.
- Attempted-not-reproducible/promoted rows: `20/0`.
- Command-mapped rows: `20`.
- Ready commands/mapped external rows: `13/20`.
- Command traceability unique/traced/declared/mismatch rows: `20/32/32/0`.
- OC4 aliases blocker/status/closure/allowed-now: `OC4/open/remain_open_ready_for_authorized_execution_not_executed_not_promoted/False`.
- OC4 ready-command and traceability aliases: `13/20/20/32/32/0`.
- Rows with all command outputs present: `20`.
- Source-policy closed/promotion-ready rows: `0/0`.
- Blocker/status/closure decision: `OC4/open/remain_open_ready_for_authorized_execution_not_executed_not_promoted`.
- Closure allowed now / OC4 blocker open: `False/True`.
- Source-policy execution invoked/allowed now: `False/False`.
- Action boundary safe/opt-in action counts: `4/1`.
- Required approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh`.
- Top-level next safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.
- Handoff authorized/commands-not-run: `False/True`.
- Handoff status/driver: `source_policy_execution_handoff_ready_not_authorized_not_run/run_b4_source_policy_after_opt_in.sh`.
- Handoff exact approval: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`.
- Handoff driver requires exact approval/does not authorize: `True/True`.
- Handoff opt-in commands/mapped rows/terminal unable rows: `13/20/20`.

## Source Roots

| suite | exists | python files | digest |
|---|---:|---:|---|
| `ra2021_absolute_coordinate` | `True` | `49` | `b7ccce0a35dfbc01e0c2654801d947fd5bc31261990b1971732dca6e43093d9f` |
| `hi2022_half_implicit` | `True` | `42` | `05c17719f26bd0f6dd3401f701f7a59ef60b50863f95bf1a777371c51312100d` |

## Suite Summary

| rows | preflight | public-root | command-mapped | unable | closed | promotion-ready |
|---:|---:|---:|---:|---:|---:|---:|
| `16` | `16` | `0` | `0` | `16` | `0` | `0` |
| `12` | `12` | `12` | `12` | `0` | `0` | `0` |
| `8` | `8` | `8` | `8` | `0` | `0` | `0` |
| `4` | `4` | `0` | `0` | `4` | `0` | `0` |

## Boundary

- `provenance_preflight_complete_is_not_source_policy_closure=True`.
- `source_policy_promotion_still_requires_authorized_closeout_or_new_artifact=True`.
- B4/B7 can close now under full source-policy: `False/False`.
