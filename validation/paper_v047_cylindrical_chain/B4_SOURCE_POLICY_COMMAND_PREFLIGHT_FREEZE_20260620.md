# B4 Source-Policy Command Preflight Freeze 20260620

Status: `command_preflight_frozen_not_authorized_not_run_not_promoted`.

This is a read-only command fingerprint and artifact-state freeze. It does not authorize or run B4 source-policy commands.

- Ready command batches/commands/mapped rows: `2/13/20`.
- Unique mapped RA/HI rows: `20`.
- Row references declared/traced/mismatched: `32/32/0`.
- Preflight parse/shell-safe/dry-run-only counts: `13/13/13`.
- Commands executed by packet/freezer: `0/False`.
- Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.
- Required approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh`.
- Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.
- Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.
- Expected artifacts existing/nonempty/total: `21/21/21`.
- Source-policy rows closed/total: `0/40`.
- Freeze digest: `c96dc1fc186bba679f4feb1ffdd21e45dd28343b11e2b3545776e65d01426433`.

## Command Fingerprints

| command id | rows | command sha256 | record sha256 |
|---|---:|---|---|
| `ra2021_public_timing_all_forms_models` | `12` | `b27efd09b21c3d72` | `8e2277aaaf8d1579` |
| `gauss6_public_single_source_policy_trio` | `3` | `020d5fddf062ff2f` | `b3be3b8c31c4b6c0` |
| `ra2021_double_order_all_forms` | `3` | `612f361552ea4905` | `a9f88164b1f4fd21` |
| `gauss6_public_four_link_source_policy_trio` | `3` | `ecce8973681bc5be` | `d19a851d672d0a2a` |
| `gauss6_public_slider_crank_source_policy_trio` | `3` | `8167aa1848522df8` | `a7d7e4e0ffa65c1c` |
| `hi2022_selected_t8_rA_half_single_pendulum` | `1` | `9c549988321afc52` | `9508387ae3203afe` |
| `hi2022_selected_t8_rA_half_double_pendulum` | `1` | `41b9ff939e7b3f27` | `2434cef572891b0a` |
| `hi2022_selected_t8_rA_half_four_link` | `1` | `ee83b583fdf70fce` | `6fcda1be127c0eab` |
| `hi2022_selected_t8_rA_half_slider_crank` | `1` | `3006d4c9b604685c` | `1c18856b870ab230` |
| `hi2022_selected_t8_rA_single_pendulum` | `1` | `3fbdeaba176afc9c` | `ef9f6c48b6727542` |
| `hi2022_selected_t8_rA_double_pendulum` | `1` | `fe591c5fd4357ca2` | `af925b545343a857` |
| `hi2022_selected_t8_rA_four_link` | `1` | `849c11e4e21d712e` | `0d72aaa4f576ed46` |
| `hi2022_selected_t8_rA_slider_crank` | `1` | `8426f85ece11fd97` | `bcfb5b4757d51463` |

## Required Opt-In Boundary

`I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`

Rows remain unclosed until authorized execution and a post-execution promotion audit explicitly promote them.
