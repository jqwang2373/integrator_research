# v029 Double-Revolute PivotVA DAE

Purpose: move beyond the single-body revolute pendulum by testing a two-body
absolute-coordinate quaternion DAE with two revolute joints:

```text
ground -- revolute -- body 1 -- revolute -- body 2
```

The stage unknowns are:

```text
body1: u, r, v, w, a, alpha
body2: u, r, v, w, a, alpha
joint multipliers: ground force/axis + interbody force/axis
```

The raw residual has 46 unknowns and 46 equations per stage. `*_pivotva`
replaces body position and velocity collocation with ground/interbody pivot
velocity and acceleration constraints. `*_fullva` also enforces hinge-axis
velocity and acceleration components explicitly while keeping the system square.

The formal run is deliberately shorter than the one-body studies because the
Gauss6 FullVA Jacobian is 138 by 138 per Newton iteration.

Run:

```bash
../.venv_sbel/bin/python run_v029.py
```

Primary outputs:

- `results/v029_report.md`
- `results/summary_v029.json`
- `results/double_revolute_pivotva_runs.csv`
- `results/double_revolute_convergence.png`
- `results/double_revolute_velocity_constraints.png`
