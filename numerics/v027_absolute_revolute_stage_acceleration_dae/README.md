# v027 Absolute-Coordinate Revolute Stage-Acceleration DAE

Purpose: test a stricter square stage-level residual for the v023/v026
absolute-coordinate quaternion revolute DAE, while preserving raw Gauss,
v026 PivotVC, and projected Gauss6 baselines.

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
constraint. The new `*_pivotva` methods additionally replace stage `v`
collocation with the pivot acceleration constraint:

```text
v + R (w x s) = 0
a + R (alpha x s + w x (w x s)) = 0
```

This keeps the Newton system square and tests whether velocity plus acceleration
consistency improves v026 without using step-after projection. Endpoint velocity
and stage velocity/acceleration parts are reported separately.

Run:

```bash
../.venv_sbel/bin/python run_v027.py
```

Primary outputs:

- `results/v027_report.md`
- `results/summary_v027.json`
- `results/absolute_revolute_stage_acceleration_runs.csv`
- `results/absolute_revolute_stage_acceleration_convergence.png`
- `results/absolute_revolute_stage_acceleration_constraints.png`
