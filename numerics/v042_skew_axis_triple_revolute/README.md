# v042 Skew-Axis Triple Revolute

This version follows v041.

v041 validated sparse-pattern caching on a planar-ish triple-revolute chain.
v042 changes the lower-pair geometry: interbody revolute axis constraints now
align each child proximal axis with the parent body's distal axis, and those
axes are intentionally skewed in body coordinates. This is a short-horizon
non-coplanar lower-pair stress test for the same quaternion Gauss6 FullVA and
sparse-AD backend.

Run:

```bash
../.venv_sbel/bin/python run_v042.py
```

Main outputs:

- `results/v042_report.md`
- `results/summary_v042.json`
- `results/skew_axis_triple_runs.csv`
- `results/skew_axis_triple_runtime.png`
- `results/skew_axis_triple_patterns.png`
