# B4 Existing-Artifact Promotion Audit

Status: `no_existing_artifact_promotable_without_new_source_policy_execution`.

This is a read-only audit over existing artifacts. It does not run source-policy numerical experiments.

- Candidate items: `8`.
- Promotion-ready without new execution: `0`.
- B4/B7 closing items: `0/0`.
- Source-policy rows closed by existing artifacts: `0/40`.
- Heavy/run_v047/v048 invoked: `False/False/False`.
- TFE execution preflight status/ready/promote/blocks: `terminal_no_public_code_self_reproduction_attempted_not_promoted/False/False/4`.
- TFE execution preflight reopen condition: `new_public_or_source_code_equivalent_tfe_implementation_artifact`.

| item | existing rows | source rows closed | promotion-ready | B4/B7 close | first blocker |
|---|---:|---:|---:|---:|---|
| `ra2021_public_baseline_shards` | `9` | `0` | `False` | `False/False` | needs matching Gauss6/FullVA local source-policy rows |
| `gauss6_public_horizon_local_rows` | `9` | `0` | `False` | `False/False` | single-pendulum local rows need matching accepted RA2021 baseline work/error rows in the same figure policy |
| `ra2021_closed_loop_same_window_work_precision` | `24` | `0` | `False` | `False/False` | same-window public work/precision rows are available for four-link and slider-crank |
| `ra2021_double_local_source_policy_candidate` | `3` | `0` | `False` | `False/False` | source-policy rows are complete but not yet independently rerun |
| `hi2022_full_t8_selected_candidate` | `24` | `0` | `False` | `False/False` | full HI2022 public step grid is not selected or not completed |
| `hi2022_b4_b7_figure_scope_demotion` | `24` | `0` | `False` | `False/False` | HI2022 full T=8 public grid remains incomplete |
| `tfe_same_test_and_runner_preflight` | `18` | `0` | `False` | `False/False` | brown_mcphee_source_code_equivalent_law_open |
| `vp2024_common_reference_proxy_and_public_recheck` | `4` | `0` | `False` | `False/False` | distinct_public_vp2024_code_path_not_found |

Next required action: run or explicitly demote source-policy work/precision lanes; current artifacts remain diagnostic, incomplete, mixed-policy, or below acceptance.
