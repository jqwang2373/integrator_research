# v040 Generated Block Triple Pattern

This version follows v039.

v039 moved the sparse-AD benchmark to a real three-body triple-revolute chain,
but its JVP-pruned discovery started from a temporary full matrix superset.
v040 replaces that with a generated block-dependency superset for the same
207-variable Gauss6 FullVA Newton system, then prunes inside that superset with
batched JVPs.

Run:

```bash
../.venv_sbel/bin/python run_v040.py
```

Main outputs:

- `results/v040_report.md`
- `results/summary_v040.json`
- `results/generated_block_triple_runs.csv`
- `results/generated_block_triple_runtime.png`
- `results/generated_block_triple_patterns.png`
