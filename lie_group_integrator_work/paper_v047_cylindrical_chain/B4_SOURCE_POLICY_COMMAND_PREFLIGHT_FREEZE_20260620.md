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
- Freeze digest: `3d2cc59263f854daf0fa269f39cbf909248b3831397e82fad5423cde21185710`.

## Command Fingerprints

| command id | rows | command sha256 | record sha256 |
|---|---:|---|---|
| `ra2021_public_timing_all_forms_models` | `12` | `4872c6ff8ada6dc2` | `ecc0c027b17a375c` |
| `gauss6_public_single_source_policy_trio` | `3` | `2bc04a8f875d704b` | `24e4561bf08b5786` |
| `ra2021_double_order_all_forms` | `3` | `69cea63fd1a40dbe` | `cd387223b4f4d2b8` |
| `gauss6_public_four_link_source_policy_trio` | `3` | `146389559565597f` | `b5ba129c3b8c2d60` |
| `gauss6_public_slider_crank_source_policy_trio` | `3` | `96c10935d8a75264` | `ce7d39468d96b44a` |
| `hi2022_selected_t8_rA_half_single_pendulum` | `1` | `8b42d3708bb6059b` | `a936db105b96d9ac` |
| `hi2022_selected_t8_rA_half_double_pendulum` | `1` | `5224d8db4c77c6d5` | `be77b3a058ba4a8e` |
| `hi2022_selected_t8_rA_half_four_link` | `1` | `58c36666b6944d5e` | `5d40ade07b51bb88` |
| `hi2022_selected_t8_rA_half_slider_crank` | `1` | `565033ff4f01346f` | `df21c0453a521aa6` |
| `hi2022_selected_t8_rA_single_pendulum` | `1` | `940d3abf456f02b6` | `779d7182c356d1a2` |
| `hi2022_selected_t8_rA_double_pendulum` | `1` | `4a73b1992589a58e` | `4ddaaad944dfe055` |
| `hi2022_selected_t8_rA_four_link` | `1` | `8b58b3b2309db01d` | `dd6f52f2e2646811` |
| `hi2022_selected_t8_rA_slider_crank` | `1` | `27fb206afce624dd` | `cea87498b22556f1` |

## Required Opt-In Boundary

`I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`

Rows remain unclosed until authorized execution and a post-execution promotion audit explicitly promote them.
