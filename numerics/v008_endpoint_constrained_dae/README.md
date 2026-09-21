# v008 Endpoint-Constrained Absolute DAE Prototype

Purpose: internalize the endpoint algebraic constraints that v007 handled by a
post-step projection.

Model:
- same fixed-pivot rigid body as v006/v007;
- two Gauss stages still solve absolute-coordinate DAE residuals with explicit
  Lagrange multipliers;
- endpoint variables `u_end, r_end, v_end, omega_end` are included directly in
  the nonlinear solve;
- endpoint equations enforce the Lie/quadrature update for attitude and angular
  velocity and enforce `r_end + R_end s = 0`,
  `v_end + R_end (omega_end x s) = 0`.

This is not yet the final frictional TFE method. It is a smaller endpoint
algebraic closure that removes post-projection while preserving the high-order
SO(3) and multiplier stage behavior found in v007.

Run:

```bash
../.venv_sbel/bin/python run_v008.py
```

Outputs are written under `results/`.
