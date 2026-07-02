# Source-Policy Reopen-Condition Monitor 2026-06-20

Status: `reopen_conditions_monitored_no_positive_source_artifact_source_policy_open`.

This read-only monitor checks whether the terminal TFE/VP source-policy suites have a current local or public-refresh reason to reopen. It does not prove global absence and does not close source-policy rows.

- Rows monitored: `20`.
- Unable-to-reproduce rows retained: `20`.
- Source-policy rows closed/promoted: `0/0`.
- Source-policy closed/open: `False/True`.
- Source-policy closed ratio: `0/20`.
- Terminal reopen conditions: `tfe2026_original_pendulum=new_public_or_source_code_equivalent_tfe_implementation_artifact; vp2024_velocity_partitioning=new_distinct_public_vp2024_velocity_partitioning_code_path`.
- Local scan digest: `f31cbb9cb18b03c9ecfd5aad29ea57e7262efa616c87ddd10a9f0796403cd208`.
- Monitor evidence digest: `839ff14d373484025bcfa046dc7bfa9a4992514e33f8aff544be01429becc0df`.
- Source artifact digest policy: hashed `SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json,SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json`; excluded `FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json`.
- Public refresh status/date/queries/positive: `public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce/2026-06-20/11/0`.
- Latest external probe date/count/positive/closed/access-limited/global-absence/reopened: `2026-06-21/9/0/0/4/False/False`.
- Latest external probe marker: `2026-06-21/9/0/0/4/False/False`.
- Public refresh local-positive/reopen-triggered aliases: `0/False`.
- Local positive reopen artifact rows: `0`.
- Source-policy reopen triggered: `False`.
- Full archive ready now: `False`.
- Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.
- Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.
- Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.
- Heavy/run_v047/v048/B4 invoked: `False/False/False/False`.

## Local External Mirror Scan

| root | exists | text files | TFE token hits | VP token hits |
|---|---:|---:|---:|---:|
| `external/sbel-reproducibility` | `True` | `165` | `0` | `0` |
| `external/public-metadata` | `True` | `0` | `0` | `0` |

## Monitored Suites

| suite | rows | unable | public positive | local token hits | reopen triggered | reopen condition |
|---|---:|---:|---:|---:|---:|---|
| `tfe2026_original_pendulum` | `16` | `16` | `False` | `0` | `False` | `new_public_or_source_code_equivalent_tfe_implementation_artifact` |
| `vp2024_velocity_partitioning` | `4` | `4` | `False` | `0` | `False` | `new_distinct_public_vp2024_velocity_partitioning_code_path` |
