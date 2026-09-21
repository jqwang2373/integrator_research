# v037 JVP-Pruned Symbolic Pattern

This version follows v036.

v036 removed dense warm-up pattern discovery by using a conservative
block-symbolic sparsity mask, but that mask was overcolored. v037 uses the
block-symbolic mask as a safe superset and then prunes it with batched JVPs
during a short Newton/trajectory dry-run. The pruned pattern is checked against
dense Jacobians after construction, but dense Jacobians are not used to build
the pruned pattern.

Run:

```bash
../.venv_sbel/bin/python run_v037.py
```

Main outputs:

- `results/v037_report.md`
- `results/summary_v037.json`
- `results/double_revolute_jvp_pruned_pattern_runs.csv`
- `results/double_revolute_jvp_pruned_pattern_runtime.png`
- `results/double_revolute_jvp_pruned_pattern_stats.png`

