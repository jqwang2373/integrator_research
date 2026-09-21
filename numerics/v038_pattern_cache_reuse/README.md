# v038 Pattern Cache Reuse

This version follows v037.

v037 recovered the fine sparse pattern without dense Jacobian discovery. v038
tests whether that pattern can be cached and reused: it discovers one
JVP-pruned pattern from the smooth double-revolute case over a short dry-run and
then reuses it for smooth and sharp cases over a longer validation horizon.
Dense Jacobian patterns are computed only after the fact to check whether the
cached pattern missed any entries.

Run:

```bash
../.venv_sbel/bin/python run_v038.py
```

Main outputs:

- `results/v038_report.md`
- `results/summary_v038.json`
- `results/double_revolute_cached_pattern_reuse_runs.csv`
- `results/double_revolute_cached_pattern_reuse_runtime.png`
- `results/double_revolute_cached_pattern_reuse_missing.png`

