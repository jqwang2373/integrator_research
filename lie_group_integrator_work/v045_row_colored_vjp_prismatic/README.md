# v045 Row-Colored VJP Prismatic Sparse AD

v044 showed that the double-prismatic interbody residual has an exact
JVP-pruned pattern, but column coloring needs 90 seeds. This version keeps the
same 138D Gauss6 FullVA residual and the same exact sparse pattern, then
assembles the Jacobian with row-colored batched VJP.

Run:

```bash
../.venv_sbel/bin/python run_v045.py
```

Outputs:

- `results/v045_report.md`
- `results/summary_v045.json`
- `results/row_vjp_prismatic_runs.csv`
- `results/row_vjp_runtime.png`
- `results/row_vjp_colors.png`
