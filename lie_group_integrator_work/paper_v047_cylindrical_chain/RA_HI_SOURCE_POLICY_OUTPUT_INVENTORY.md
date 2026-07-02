# RA/HI Source-Policy Output Inventory

Status: `existing_expected_outputs_present_not_promotion_evidence`.

This read-only inventory hashes and counts the expected RA/HI output artifacts. It does not run guarded commands and does not promote rows.

- Commands/outputs/summaries: `13`/`13`/`8`.
- CSV data rows: `54`.
- HI2022 summary ok/closed rows: `22`/`0`.
- Promotion-ready/full-grid/coarse-trio summaries: `0`/`0`/`8`.
- Source-policy rows closed by inventory: `0`.
- Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.
- Safe action ids: `['rebuild_read_only_audit_chain', 'rerun_read_only_validators', 'keep_narrowed_archive_provenance_only', 'monitor_reopen_conditions']`; opt-in action ids: `['authorized_b4_ra_hi_source_policy_execution']`.
- Source-policy execution handoff exact approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh/True/True/13/20/20`.
- Source-policy execution handoff authorized/commands-not-run: `False/True`.

| suite | command | output rows | summary status |
|---|---|---:|---|
| `ra2021_absolute_coordinate` | `ra2021_public_timing_all_forms_models` | `12` | `none` |
| `ra2021_absolute_coordinate` | `gauss6_public_single_source_policy_trio` | `3` | `none` |
| `ra2021_absolute_coordinate` | `ra2021_double_order_all_forms` | `9` | `none` |
| `ra2021_absolute_coordinate` | `gauss6_public_four_link_source_policy_trio` | `3` | `none` |
| `ra2021_absolute_coordinate` | `gauss6_public_slider_crank_source_policy_trio` | `3` | `none` |
| `hi2022_half_implicit` | `hi2022_selected_t8_rA_half_single_pendulum` | `3` | `executed_full_T8_selected_coarse_trio_not_promoted` |
| `hi2022_half_implicit` | `hi2022_selected_t8_rA_half_double_pendulum` | `3` | `partial_or_failed_full_T8_source_policy_candidate_not_promoted` |
| `hi2022_half_implicit` | `hi2022_selected_t8_rA_half_four_link` | `3` | `executed_full_T8_selected_coarse_trio_not_promoted` |
| `hi2022_half_implicit` | `hi2022_selected_t8_rA_half_slider_crank` | `3` | `executed_full_T8_selected_coarse_trio_not_promoted` |
| `hi2022_half_implicit` | `hi2022_selected_t8_rA_single_pendulum` | `3` | `executed_full_T8_selected_coarse_trio_not_promoted` |
| `hi2022_half_implicit` | `hi2022_selected_t8_rA_double_pendulum` | `3` | `executed_full_T8_selected_coarse_trio_not_promoted` |
| `hi2022_half_implicit` | `hi2022_selected_t8_rA_four_link` | `3` | `executed_full_T8_selected_coarse_trio_not_promoted` |
| `hi2022_half_implicit` | `hi2022_selected_t8_rA_slider_crank` | `3` | `executed_full_T8_selected_coarse_trio_not_promoted` |
