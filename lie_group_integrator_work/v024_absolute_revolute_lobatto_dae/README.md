# v024 Absolute-Coordinate Revolute Lobatto DAE

Purpose: extend v023's absolute-coordinate quaternion revolute DAE with
Lobatto endpoint-node collocation, while preserving the Gauss interior-node
methods as baselines.

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

Lobatto includes stages at `c=0` and `c=1`, so this version also adds local
zero-safe JAX quaternion exponential and right-Jacobian inverse functions. This
avoids the undefined derivative of `norm(u)` at the zero local rotation
increment.

This version intentionally does not endpoint-project. For Lobatto, the endpoint
is the final collocation node, so endpoint position constraints are enforced by
the stage residual. Endpoint velocity constraint errors are still diagnostics.

Run:

```bash
../.venv_sbel/bin/python run_v024.py
```

Primary outputs:

- `results/v024_report.md`
- `results/summary_v024.json`
- `results/absolute_revolute_lobatto_runs.csv`
- `results/absolute_revolute_lobatto_convergence.png`
- `results/absolute_revolute_lobatto_constraints.png`
