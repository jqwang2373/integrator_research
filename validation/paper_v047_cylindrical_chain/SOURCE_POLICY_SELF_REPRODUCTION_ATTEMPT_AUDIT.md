# Source-Policy Self-Reproduction Attempt Audit

Status: `nonpublic_code_rows_attempted_not_reproducible_not_promoted`.

Rows without a usable public implementation are now explicitly attempted and dispositioned.
A row marked `attempted_not_reproducible` is not promoted, not source-policy closed, and not external-superiority evidence.

- Rows audited: `20`.
- Self-reproduction attempted rows: `20`.
- Attempted-not-reproducible rows: `20`.
- Unable-to-reproduce rows: `20`.
- Source-policy closed rows: `0`.
- External-superiority ready rows: `0`.
- Open execution-queue rows from this audit: `0`.
- Heavy/run_v047/v048 invoked: `False/False/False`.

## Suite Summary

| suite | rows | attempted | not reproducible | unable to reproduce | closed | external ready | open execution |
|---|---:|---:|---:|---:|---:|---:|---:|
| `tfe2026_original_pendulum` | `16` | `16` | `16` | `16` | `0` | `0` | `0` |
| `vp2024_velocity_partitioning` | `4` | `4` | `4` | `4` | `0` | `0` | `0` |

## Row Disposition

| suite | method | example | disposition | primary reason |
|---|---|---|---|---|
| `tfe2026_original_pendulum` | `tfe2026_Newmark_beta` | `single_pendulum` | `attempted_not_reproducible` | `paper_spec_candidate_runner_not_source_policy_equivalent` |
| `tfe2026_original_pendulum` | `tfe2026_Newmark_beta` | `double_pendulum` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_original_pendulum` | `tfe2026_Newmark_beta` | `four_link` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_original_pendulum` | `tfe2026_Newmark_beta` | `slider_crank` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m1` | `single_pendulum` | `attempted_not_reproducible` | `paper_spec_candidate_runner_not_source_policy_equivalent` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m1` | `double_pendulum` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m1` | `four_link` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m1` | `slider_crank` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m2` | `single_pendulum` | `attempted_not_reproducible` | `paper_spec_candidate_runner_not_source_policy_equivalent` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m2` | `double_pendulum` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m2` | `four_link` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m2` | `slider_crank` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_original_pendulum` | `tfe2026_trapezoidal` | `single_pendulum` | `attempted_not_reproducible` | `paper_spec_candidate_runner_not_source_policy_equivalent` |
| `tfe2026_original_pendulum` | `tfe2026_trapezoidal` | `double_pendulum` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_original_pendulum` | `tfe2026_trapezoidal` | `four_link` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_original_pendulum` | `tfe2026_trapezoidal` | `slider_crank` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `vp2024_velocity_partitioning` | `vp2024_coordinate_partitioning_rA` | `single_pendulum` | `attempted_not_reproducible` | `distinct_public_vp2024_code_path_not_found_proxy_not_source_policy` |
| `vp2024_velocity_partitioning` | `vp2024_coordinate_partitioning_rA` | `double_pendulum` | `attempted_not_reproducible` | `distinct_public_vp2024_code_path_not_found_proxy_not_source_policy` |
| `vp2024_velocity_partitioning` | `vp2024_coordinate_partitioning_rA` | `four_link` | `attempted_not_reproducible` | `distinct_public_vp2024_code_path_not_found_proxy_not_source_policy` |
| `vp2024_velocity_partitioning` | `vp2024_coordinate_partitioning_rA` | `slider_crank` | `attempted_not_reproducible` | `distinct_public_vp2024_code_path_not_found_proxy_not_source_policy` |
