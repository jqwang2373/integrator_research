# v028 Off-Axis Revolute Full-Axis DAE

Purpose: stress-test v027 under a non-hinge body torque and test a stricter
square full-axis residual for the absolute-coordinate quaternion revolute DAE.
The method set preserves raw Gauss, v026 PivotVC, and v027 PivotVA baselines.

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
stage reaction-force norm. A constant off-axis body torque is also applied so
the constrained-axis multipliers must do nontrivial work. JAX differentiates the
whole coupled residual.

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

The new `*_fullva` methods also replace the x/z orientation and angular-velocity
collocation equations with hinge-axis velocity and acceleration constraints:

```text
R (w x e_y) projected to x/z = 0
R (alpha x e_y + w x (w x e_y)) projected to x/z = 0
```

Only the hinge y-components of orientation and angular-velocity collocation are
kept. This is still a square residual, but it is revolute-specific.

Run:

```bash
../.venv_sbel/bin/python run_v028.py
```

Primary outputs:

- `results/v028_report.md`
- `results/summary_v028.json`
- `results/offaxis_revolute_full_axis_runs.csv`
- `results/offaxis_revolute_full_axis_convergence.png`
- `results/offaxis_revolute_full_axis_velocity_constraints.png`
- `results/offaxis_revolute_full_axis_acceleration_constraints.png`
