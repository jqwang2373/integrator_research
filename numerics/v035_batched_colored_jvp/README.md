# v035 Batched Colored JVP

This version follows v034 directly.

v034 proved that column-colored JAX JVP sparse Jacobian assembly is correct for
the double-revolute Gauss6 FullVA residual, but the implementation used one JVP
dispatch per color. v035 keeps the same residual, sparsity pattern, and CSR
Newton solve, then replaces those separate dispatches with one compiled
`vmap(jvp)` batch over all color seed vectors.

Run:

```bash
../.venv_sbel/bin/python run_v035.py
```

Main outputs:

- `results/v035_report.md`
- `results/summary_v035.json`
- `results/double_revolute_batched_colored_jvp_runs.csv`
- `results/double_revolute_batched_colored_jvp_runtime.png`
- `results/double_revolute_batched_colored_jvp_accuracy.png`

