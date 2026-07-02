# v039 Triple-Revolute Scaling

This version follows v038.

v038 validated cached sparse pattern reuse on the two-body double-revolute
benchmark. v039 moves to a real larger topology: a three-body, three-joint
triple-revolute chain with Brown-McPhee friction at every hinge. The Gauss6
FullVA Newton system grows from 138 variables to 207 variables.

Run:

```bash
../.venv_sbel/bin/python run_v039.py
```

Main outputs:

- `results/v039_report.md`
- `results/summary_v039.json`
- `results/triple_revolute_scaling_runs.csv`
- `results/triple_revolute_scaling_runtime.png`

