# Global Comparison Policy Audit

Reasonable apples-to-apples claims: `True`.
Passed requirements: `14/14`.
Common-reference apples-to-apples rows: `44/44`.
Mixed-policy direct error rows allowed: `0`.
Direct error rows allowed: `40`.
Paper direct error rows allowed: `0`.
Source-policy reproduction: `False`.
Public-code fixed-grid replay: `True`.
External superiority claim: `False`.

| Requirement | status | evidence | interpretation |
|---|---:|---|---|
| `common_reference_direct_error_claim_is_bounded_not_paper_superiority` | `pass` | `common_reference_error_summary.{json,csv,md}; all_examples_apples_to_apples_forensic_audit.{json,md}` | fixed-grid common-reference arithmetic is bounded diagnostic evidence, not a paper-level external-superiority claim |
| `all_examples_all_methods_forensic_audit_blocks_external_error_claim` | `pass` | `all_examples_apples_to_apples_forensic_audit.{json,csv,md}` | all four examples and all 44 common-reference method/example cells were checked; no strict external error claim is allowed |
| `row_level_apples_to_apples_policy_passes` | `pass` | `apples_to_apples_policy_audit.{json,csv}` | every common-reference summary row shares h-grid, t_end, reference policy, norm, and fixed-grid public replay when needed |
| `mixed_policy_direct_error_is_blocked` | `pass` | `error_reference_policy_audit.{json,md}` | the main coarse table may support order comparisons, but its mixed-reference error columns are not direct cross-method error claims |
| `coarse_conclusion_uses_current_common_reference_numbers` | `pass` | `coarse_four_example_order_conclusion.md` | the conclusion common-reference section was regenerated after fixed-grid replay and no longer carries the old Dan/Kissel/Negrut negative-order contamination |
| `main_coarse_table_is_not_blanket_error_superiority` | `pass` | `coarse_four_example_order_summary.{json,md}; coarse_four_example_order_conclusion.md` | the coarse matrix reports observed order and row-local errors; direct common-reference error wins remain bounded diagnostics |
| `vp_error_order_boundary_is_preserved` | `pass` | `vp_coordinate_partitioning_order_audit.json; large_step_vp_local_order_summary.json` | VP rows preserve the distinction between higher observed order and not winning every reported finest-step error |
| `large_step_vp_direct_error_not_overclaimed` | `pass` | `error_reference_policy_audit.json; large_step_vp_local_order_summary.md` | larger-step VP diagnostics support an order claim, not a universal direct-error claim |
| `coverage_matrix_not_same_test_superiority` | `pass` | `four_example_performance_summary.json; four_example_performance_matrix.md` | the broad performance matrix is a coverage ledger and does not merge source policies into one same-test claim |
| `baseline_resolution_scope_is_explicit` | `pass` | `baseline_coverage_matrix.{json,md}` | VP is an alias-resolved method row and TFE(m=3) four-link is excluded; direct-error wording is bounded by the forensic audit |
| `closed_loop_strict_common_reference_not_external_superiority` | `pass` | `closed_loop_true_dynamic_strict_common_reference.{json,md}` | closed-loop strict common-reference rows remove a local caveat for two examples but still do not claim full external superiority |
| `same_window_and_public_work_rows_are_bounded` | `pass` | `closed_loop_true_dynamic_public_work_precision.json; single_pendulum_coarse_same_window_work_precision_summary.json` | same-window work/precision rows are labeled as bounded evidence, not final external superiority |
| `dan_single_repair_is_scoped` | `pass` | `dan_single_pendulum_reference_policy_audit.json` | the repaired Dan/Kissel/Negrut single-pendulum rows are scoped to fixed-grid apples-to-apples evidence only |
| `global_external_superiority_not_claimed` | `pass` | `72 result markdown/json files; summary_v048.json; v048_report.md` | no generated result artifact claims full external superiority or a completed same-test campaign |

The fixed-grid common-reference matrix is a bounded diagnostic. The all-example forensic audit blocks paper-level direct error superiority until source-policy reproduction, velocity/output mapping, original TFE setup, and VP code-path issues are closed.
