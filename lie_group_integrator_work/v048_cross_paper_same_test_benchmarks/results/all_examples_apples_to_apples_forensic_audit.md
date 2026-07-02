# All-Examples Apples-To-Apples Forensic Audit

Status: **all_examples_all_methods_checked_source_policy_open**.

- Examples checked: `double_pendulum, four_link, single_pendulum, slider_crank`.
- Method/example cells checked: `44/44`.
- Raw common-reference rows checked: `132`.
- Bounded common-reference diagnostic rows: `44`.
- Strict external error-claim rows allowed: `0`.
- Direct error superiority allowed for paper: `False`.
- Source-policy reproduction: `False`.

## Per Example

| example | rows | methods | rows with issues | source-policy open | strict error-claim rows |
|---|---:|---:|---:|---:|---:|
| `single_pendulum` | `11` | `11` | `10` | `10` | `0` |
| `double_pendulum` | `11` | `11` | `10` | `10` | `0` |
| `four_link` | `11` | `11` | `10` | `10` | `0` |
| `slider_crank` | `11` | `11` | `10` | `10` | `0` |

## Issue Counts

| issue | count |
|---|---:|
| `near_floor_order_unidentifiable` | `3` |
| `negative_velocity_order` | `3` |
| `original_tfe_setup_not_encoded` | `16` |
| `position_aligned_velocity_mismatch` | `20` |
| `source_policy_not_closed` | `40` |
| `velocity_error_nonmonotone_or_floor_limited` | `5` |
| `vp2024_code_path_unresolved_or_proxy` | `4` |

## Rows

| example | method | source level | vel order | finest vel error | claim scope | issues |
|---|---|---|---:|---:|---|---|
| `double_pendulum` | `hi2022_rA` | `public_code_bounded_replay` | `1.04906` | `4.944e-05` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | source_policy_not_closed |
| `double_pendulum` | `hi2022_rA_half` | `public_code_bounded_replay` | `-0.798995` | `2.96995` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | negative_velocity_order|velocity_error_nonmonotone_or_floor_limited|source_policy_not_closed |
| `double_pendulum` | `local_Gauss6_FullVA` | `local_proposed_method` | `6.0097` | `2.346e-13` | `internal_order_evidence` | none |
| `double_pendulum` | `ra2021_rA` | `public_code_replay` | `1.05244` | `4.924e-05` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | source_policy_not_closed |
| `double_pendulum` | `ra2021_reps` | `public_code_replay` | `1.05244` | `4.924e-05` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | source_policy_not_closed |
| `double_pendulum` | `ra2021_rp` | `public_code_replay` | `0.36139` | `5.241e-05` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | velocity_error_nonmonotone_or_floor_limited|source_policy_not_closed |
| `double_pendulum` | `tfe2026_Newmark_beta` | `local_formula_proxy` | `1.78651` | `4.246e-04` | `formula_proxy_diagnostic_not_original_paper_superiority` | source_policy_not_closed|original_tfe_setup_not_encoded |
| `double_pendulum` | `tfe2026_TFE_m1` | `local_formula_proxy` | `1.99606` | `2.708e-04` | `formula_proxy_diagnostic_not_original_paper_superiority` | source_policy_not_closed|original_tfe_setup_not_encoded |
| `double_pendulum` | `tfe2026_TFE_m2` | `local_formula_proxy` | `1.86993` | `8.711e-05` | `formula_proxy_diagnostic_not_original_paper_superiority` | source_policy_not_closed|original_tfe_setup_not_encoded |
| `double_pendulum` | `tfe2026_trapezoidal` | `local_formula_proxy` | `1.99966` | `2.708e-04` | `formula_proxy_diagnostic_not_original_paper_superiority` | source_policy_not_closed|original_tfe_setup_not_encoded |
| `double_pendulum` | `vp2024_coordinate_partitioning_rA` | `local_proxy_or_alias` | `1.00005` | `0.00216512` | `proxy_or_alias_diagnostic_not_original_code_superiority` | source_policy_not_closed|vp2024_code_path_unresolved_or_proxy |
| `four_link` | `hi2022_rA` | `public_code_bounded_replay` | `1.01545` | `0.197042` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed |
| `four_link` | `hi2022_rA_half` | `public_code_bounded_replay` | `1.58965` | `0.197042` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed |
| `four_link` | `local_Gauss6_FullVA` | `local_proposed_method` | `6.08482` | `1.093e-11` | `internal_order_evidence` | none |
| `four_link` | `ra2021_rA` | `public_code_replay` | `1.01545` | `0.197042` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed |
| `four_link` | `ra2021_reps` | `public_code_replay` | `2.89379` | `0.0145777` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed |
| `four_link` | `ra2021_rp` | `public_code_replay` | `2.89373` | `0.0145788` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed |
| `four_link` | `tfe2026_Newmark_beta` | `local_formula_proxy` | `1.87247` | `0.016722` | `formula_proxy_diagnostic_not_original_paper_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed|original_tfe_setup_not_encoded |
| `four_link` | `tfe2026_TFE_m1` | `local_formula_proxy` | `3.86566` | `5.253e-04` | `formula_proxy_diagnostic_not_original_paper_superiority` | source_policy_not_closed|original_tfe_setup_not_encoded |
| `four_link` | `tfe2026_TFE_m2` | `local_formula_proxy` | `1.02133` | `6.711e-04` | `formula_proxy_diagnostic_not_original_paper_superiority` | source_policy_not_closed|original_tfe_setup_not_encoded |
| `four_link` | `tfe2026_trapezoidal` | `local_formula_proxy` | `3.88811` | `5.306e-04` | `formula_proxy_diagnostic_not_original_paper_superiority` | source_policy_not_closed|original_tfe_setup_not_encoded |
| `four_link` | `vp2024_coordinate_partitioning_rA` | `local_proxy_or_alias` | `-5.332e-04` | `1.087e-08` | `proxy_or_alias_diagnostic_not_original_code_superiority` | near_floor_order_unidentifiable|negative_velocity_order|velocity_error_nonmonotone_or_floor_limited|source_policy_not_closed|vp2024_code_path_unresolved_or_proxy |
| `single_pendulum` | `hi2022_rA` | `public_code_bounded_replay` | `1.00481` | `0.0772451` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed |
| `single_pendulum` | `hi2022_rA_half` | `public_code_bounded_replay` | `1.84063` | `0.0772451` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed |
| `single_pendulum` | `local_Gauss6_FullVA` | `local_proposed_method` | `5.80133` | `1.155e-12` | `internal_order_evidence` | none |
| `single_pendulum` | `ra2021_rA` | `public_code_replay` | `0.616851` | `13.0488` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed |
| `single_pendulum` | `ra2021_reps` | `public_code_replay` | `0.616851` | `13.0488` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed |
| `single_pendulum` | `ra2021_rp` | `public_code_replay` | `0.516813` | `14.99` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed |
| `single_pendulum` | `tfe2026_Newmark_beta` | `local_formula_proxy` | `0.900797` | `14.7909` | `formula_proxy_diagnostic_not_original_paper_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed|original_tfe_setup_not_encoded |
| `single_pendulum` | `tfe2026_TFE_m1` | `local_formula_proxy` | `1.02082` | `14.9824` | `formula_proxy_diagnostic_not_original_paper_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed|original_tfe_setup_not_encoded |
| `single_pendulum` | `tfe2026_TFE_m2` | `local_formula_proxy` | `0.0537298` | `110.22` | `formula_proxy_diagnostic_not_original_paper_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed|original_tfe_setup_not_encoded |
| `single_pendulum` | `tfe2026_trapezoidal` | `local_formula_proxy` | `1.02446` | `14.9826` | `formula_proxy_diagnostic_not_original_paper_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed|original_tfe_setup_not_encoded |
| `single_pendulum` | `vp2024_coordinate_partitioning_rA` | `local_proxy_or_alias` | `6.149e-15` | `3.163e-11` | `proxy_or_alias_diagnostic_not_original_code_superiority` | near_floor_order_unidentifiable|velocity_error_nonmonotone_or_floor_limited|source_policy_not_closed|vp2024_code_path_unresolved_or_proxy |
| `slider_crank` | `hi2022_rA` | `public_code_bounded_replay` | `0.940514` | `0.0328072` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed |
| `slider_crank` | `hi2022_rA_half` | `public_code_bounded_replay` | `2.45854` | `0.0328072` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed |
| `slider_crank` | `local_Gauss6_FullVA` | `local_proposed_method` | `7.34091` | `9.189e-12` | `internal_order_evidence` | none |
| `slider_crank` | `ra2021_rA` | `public_code_replay` | `0.940524` | `0.0328068` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed |
| `slider_crank` | `ra2021_reps` | `public_code_replay` | `0.940496` | `0.032807` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed |
| `slider_crank` | `ra2021_rp` | `public_code_replay` | `0.940461` | `0.0328069` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | position_aligned_velocity_mismatch|source_policy_not_closed |
| `slider_crank` | `tfe2026_Newmark_beta` | `local_formula_proxy` | `2.05116` | `0.00153123` | `formula_proxy_diagnostic_not_original_paper_superiority` | source_policy_not_closed|original_tfe_setup_not_encoded |
| `slider_crank` | `tfe2026_TFE_m1` | `local_formula_proxy` | `2.48136` | `6.264e-04` | `formula_proxy_diagnostic_not_original_paper_superiority` | source_policy_not_closed|original_tfe_setup_not_encoded |
| `slider_crank` | `tfe2026_TFE_m2` | `local_formula_proxy` | `2.2899` | `9.881e-05` | `formula_proxy_diagnostic_not_original_paper_superiority` | source_policy_not_closed|original_tfe_setup_not_encoded |
| `slider_crank` | `tfe2026_trapezoidal` | `local_formula_proxy` | `2.32935` | `7.328e-04` | `formula_proxy_diagnostic_not_original_paper_superiority` | source_policy_not_closed|original_tfe_setup_not_encoded |
| `slider_crank` | `vp2024_coordinate_partitioning_rA` | `local_proxy_or_alias` | `-3.253e-07` | `1.332e-07` | `proxy_or_alias_diagnostic_not_original_code_superiority` | near_floor_order_unidentifiable|negative_velocity_order|velocity_error_nonmonotone_or_floor_limited|source_policy_not_closed|vp2024_code_path_unresolved_or_proxy |

## Claim Boundary

All four examples and all 44 common-reference method/example cells have been checked. The fixed-grid common-reference arithmetic is a bounded diagnostic, but it is not enough for a CMAME paper to claim external error superiority over the source papers.  Source-policy reproduction, velocity/output mapping, original TFE setup, and VP code-path questions remain open.
