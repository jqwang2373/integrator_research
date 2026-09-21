# v043 Skew Prismatic Lower Pair

This version follows v042.

v042 showed that the sparse-AD FullVA path survives skew parent-child revolute
axis constraints. v043 adds a different lower pair: a skew-axis prismatic joint
with five constraints, one free sliding coordinate, Brown-McPhee-style sliding
friction, and the same quaternion Gauss6 FullVA Newton machinery.

Run:

```bash
../.venv_sbel/bin/python run_v043.py
```

Main outputs:

- `results/v043_report.md`
- `results/summary_v043.json`
- `results/skew_prismatic_runs.csv`
- `results/skew_prismatic_runtime.png`
- `results/skew_prismatic_patterns.png`
