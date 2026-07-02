# v007 Absolute-Coordinate Gauss-Lie DAE Prototype

Purpose: move beyond v006's reduced fixed-pivot formulation and solve a true
absolute-coordinate stage system with explicit Lagrange multipliers.

Model:
- one rigid body with absolute center-of-mass coordinates `r`, attitude
  `R in SO(3)`, translational velocity `v`, and body angular velocity `omega`;
- fixed pivot holonomic constraint `g(r, R) = r + R s = 0`;
- stage unknowns include `u_i, r_i, v_i, omega_i, a_i, alpha_i, lambda_i` at the
  two Gauss-Legendre points;
- stage equations include Lie kinematics, translational dynamics, rotational
  dynamics, and position-level constraints.

This is still frictionless, but it is the first version in this workspace where
the multiplier is part of the nonlinear collocation solve rather than recovered
after a reduced solve.

Run:

```bash
../.venv_sbel/bin/python run_v007.py
```

Outputs are written under `results/`.
