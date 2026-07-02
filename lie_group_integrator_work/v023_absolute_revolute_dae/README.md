# v023 Absolute-Coordinate Revolute DAE

Purpose: move from v022's reduced one-DOF revolute Brown-McPhee model to an
absolute-coordinate quaternion DAE with an explicit revolute joint.

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

This version intentionally does not endpoint-project. Endpoint position and
velocity constraint errors are reported as diagnostics.

Run:

```bash
../.venv_sbel/bin/python run_v023.py
```

Primary outputs:

- `results/v023_report.md`
- `results/summary_v023.json`
- `results/absolute_revolute_dae_runs.csv`
- `results/absolute_revolute_dae_convergence.png`
