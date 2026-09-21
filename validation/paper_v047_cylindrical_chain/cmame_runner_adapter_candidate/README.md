# CMAME Runner Adapter Candidate

Status: runner-adapter candidate, not submission ready.

This package is a compact executable adapter. It checks the embedded 44-row
paper matrix and common-reference result audit. If a local v048 benchmark tree
is provided, it can call `run_coarse_four_example_order.py --report-only`.

It is not a self-contained simulation runner and does not close source-policy
external rows or the proof gap.

Human-runnable quickstart:

```bash
python scripts/run_four_example_matrix_adapter.py
```

Expected terminal markers:

- `cmame_runner_adapter_candidate=PASS`.
- `embedded_paper_matrix=44/44`.
- `common_reference_order_error_wins=40/40,40/40`.
- `source_policy_closed=0/40`.
- `runner_adapter_present=True`.
- `self_contained_simulation_runner=False`.
- `submission_ready=False`.

Closed-loop local four-link/slider-crank row replay:

```bash
python scripts/replay_closed_loop_local_rows.py
```

Expected terminal markers:

- `cmame_closed_loop_local_rows_replay=PASS`.
- `models=four_link,slider_crank`.
- `local_rows=6/6`.
- `summary_json=results/closed_loop_local_rows_summary.json`.
- `rows_csv=results/closed_loop_local_rows.csv`.
- `self_contained_simulation_runner=False`.
- `source_policy_external_superiority_allowed=False`.
- `proof_gap_closed_by_adapter=False`.

Run embedded checks:

```bash
python scripts/run_four_example_matrix_adapter.py
```

Optional local v048 report-only call:

```bash
python scripts/run_four_example_matrix_adapter.py --external-v048-root ../../../numerics/v048_cross_paper_same_test_benchmarks
```
