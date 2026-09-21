# B4 Source-Policy Expected Output Schema Audit 20260620

Status: `expected_outputs_schema_ready_not_authorized_not_run_not_promoted`.

This is a read-only schema audit of expected B4 output artifacts. It does not authorize or run B4 source-policy commands, and it closes zero source-policy rows.

- Commands/CSV summaries/JSON summaries/artifacts: `13/13/8/21`.
- Artifacts existing/nonempty/size-match/hash-match: `21/21/21/21`.
- Parseable CSV/JSON summary artifacts: `13/8`.
- Schema-ready commands: `13/13`.
- Command traceability shell/output/summary/no-summary/existing-output/existing-summary: `13/13/8/5/13/8`.
- Total CSV data rows: `54`.
- Commands executed / source-policy rows closed / promotion-ready rows: `False/0/0`.
- Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.
- Required approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh`.
- Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.
- Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.
- Submission ready: `False`.

| Command | Expected CSV | Expected summary | CSV rows | CSV columns | CSV status counts | Summary status | Schema status |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| `ra2021_public_timing_all_forms_models` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/ra2021_public_timing_rows.csv` | `none` | `12` | `16` | `{"ok": 12}` | `none` | `schema_ready` |
| `gauss6_public_single_source_policy_trio` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/gauss6_fullva_public_horizon_single_rows.csv` | `none` | `3` | `32` | `{"ok": 3}` | `none` | `schema_ready` |
| `ra2021_double_order_all_forms` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/ra2021_double_pendulum_order_rows.csv` | `none` | `9` | `23` | `{"ok": 9}` | `none` | `schema_ready` |
| `gauss6_public_four_link_source_policy_trio` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/public_closed_loop_shards/four_link_1em02_1em03_1em04.csv` | `none` | `3` | `38` | `{"ok": 3}` | `none` | `schema_ready` |
| `gauss6_public_slider_crank_source_policy_trio` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/public_closed_loop_shards/slider_crank_1em02_1em03_1em04.csv` | `none` | `3` | `38` | `{"ok": 3}` | `none` | `schema_ready` |
| `hi2022_selected_t8_rA_half_single_pendulum` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_half_single_pendulum_rows.csv` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_half_single_pendulum_summary.json` | `3` | `34` | `{"ok": 3}` | `executed_full_T8_selected_coarse_trio_not_promoted` | `schema_ready` |
| `hi2022_selected_t8_rA_half_double_pendulum` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_half_double_pendulum_rows.csv` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_half_double_pendulum_summary.json` | `3` | `34` | `{"failed:RuntimeError:Newton-Raphson not converging at t: 2.240, k: 100": 1, "failed:RuntimeError:Newton-Raphson not converging at t: 5.800, k: 100": 1, "ok": 1}` | `partial_or_failed_full_T8_source_policy_candidate_not_promoted` | `schema_ready` |
| `hi2022_selected_t8_rA_half_four_link` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_half_four_link_rows.csv` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_half_four_link_summary.json` | `3` | `34` | `{"ok": 3}` | `executed_full_T8_selected_coarse_trio_not_promoted` | `schema_ready` |
| `hi2022_selected_t8_rA_half_slider_crank` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_half_slider_crank_rows.csv` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_half_slider_crank_summary.json` | `3` | `34` | `{"ok": 3}` | `executed_full_T8_selected_coarse_trio_not_promoted` | `schema_ready` |
| `hi2022_selected_t8_rA_single_pendulum` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_single_pendulum_rows.csv` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_single_pendulum_summary.json` | `3` | `34` | `{"ok": 3}` | `executed_full_T8_selected_coarse_trio_not_promoted` | `schema_ready` |
| `hi2022_selected_t8_rA_double_pendulum` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_double_pendulum_rows.csv` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_double_pendulum_summary.json` | `3` | `34` | `{"ok": 3}` | `executed_full_T8_selected_coarse_trio_not_promoted` | `schema_ready` |
| `hi2022_selected_t8_rA_four_link` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_four_link_rows.csv` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_four_link_summary.json` | `3` | `34` | `{"ok": 3}` | `executed_full_T8_selected_coarse_trio_not_promoted` | `schema_ready` |
| `hi2022_selected_t8_rA_slider_crank` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_slider_crank_rows.csv` | `../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_slider_crank_summary.json` | `3` | `34` | `{"ok": 3}` | `executed_full_T8_selected_coarse_trio_not_promoted` | `schema_ready` |

The schema-ready status is a structure and fingerprint check only; post-execution promotion evidence is still required before any B4 source-policy row can close.
