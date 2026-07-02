# v025 Absolute-Coordinate Revolute Projected DAE

Purpose: add a SHAKE/RATTLE-style endpoint projection to the v023
absolute-coordinate quaternion revolute DAE, while preserving the raw Gauss
methods for comparison.

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

The projected methods map the endpoint orientation back to a pure revolute
rotation, set tangent angular velocity, and reconstruct `r` and `v` from the
constraint. Raw endpoint drift and projection correction sizes are kept as
diagnostics.

Run:

```bash
../.venv_sbel/bin/python run_v025.py
```

Primary outputs:

- `results/v025_report.md`
- `results/summary_v025.json`
- `results/absolute_revolute_projected_runs.csv`
- `results/absolute_revolute_projected_convergence.png`
- `results/absolute_revolute_projected_constraints.png`
