# v026 Absolute-Coordinate Revolute Stage-Velocity DAE

Purpose: test a square stage-level velocity-consistent residual for the v023
absolute-coordinate quaternion revolute DAE, while preserving raw Gauss methods
and the projected Gauss6 repair as baselines.

The stage unknowns are:

```text
u, r, v, w, a, alpha, lambda
```

The five revolute constraints are:

```text
r + R s = 0
(R e_y)_x = 0
(R e_y)_z = 0
```

The Brown-McPhee friction torque acts about the hinge axis and is scaled by the
stage reaction-force norm. JAX differentiates the whole coupled residual.

The `*_pivotvc` methods replace stage `r` collocation with the pivot velocity
constraint. This keeps the nonlinear system square and tests whether more
index-3 consistency can be added inside Newton without step-after projection.
Endpoint and stage pivot/axis velocity parts are reported separately.

Run:

```bash
../.venv_sbel/bin/python run_v026.py
```

Primary outputs:

- `results/v026_report.md`
- `results/summary_v026.json`
- `results/absolute_revolute_stage_velocity_runs.csv`
- `results/absolute_revolute_stage_velocity_convergence.png`
- `results/absolute_revolute_stage_velocity_constraints.png`
