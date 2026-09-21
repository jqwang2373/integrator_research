# v044 Double Prismatic Chain

This version extends v043 from a single ground prismatic joint to a two-body
chain:

- joint 0: ground-to-body prismatic joint;
- joint 1: interbody prismatic joint between body 0 and body 1.

The residual keeps the Gauss6 FullVA structure and Brown-McPhee-style sliding
friction. The main question is whether generated-block JVP-pruned sparse AD
remains exact on a 138D non-revolute lower-pair system.

Run:

```bash
../../.venv_sbel/bin/python run_v044.py
```

Outputs:

- `results/v044_report.md`
- `results/summary_v044.json`
- `results/double_prismatic_runs.csv`
- `results/double_prismatic_runtime.png`
- `results/double_prismatic_patterns.png`
