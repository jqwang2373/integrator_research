# v036 Symbolic Block Pattern

This version follows v035.

v035 made colored sparse AD fast by batching all color seed directions in one
compiled `vmap(jvp)` call, but the sparsity pattern still came from a dense
warm-up Newton path. v036 removes that dependency from the tested solver path by
building a conservative block-symbolic sparsity mask from the v029 Gauss6 FullVA
residual structure.

Run:

```bash
../.venv_sbel/bin/python run_v036.py
```

Main outputs:

- `results/v036_report.md`
- `results/summary_v036.json`
- `results/double_revolute_symbolic_block_pattern_runs.csv`
- `results/double_revolute_symbolic_block_pattern_runtime.png`
- `results/double_revolute_symbolic_block_pattern_stats.png`

